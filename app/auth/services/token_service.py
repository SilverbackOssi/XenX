from datetime import datetime, timedelta, timezone
import uuid
from typing import Optional, Dict, Any
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from fastapi import Depends, HTTPException, status
from app.auth.models.users import User
from app.auth.database import get_db
from app.config import get_settings

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
bearer_scheme = HTTPBearer()

class TokenService:
    @staticmethod
    def _create_token(data: Dict[str, Any], expires_delta: timedelta, token_type: str) -> str:
        """Internal method to create a JWT."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()), # Unique ID for the token
            "type": token_type  # Explicitly set the token type
        })
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_access_token(data: dict) -> str:
        """Create a new access token for a user."""
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return TokenService._create_token(data, expires, "access")

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a new refresh token for a user."""
        expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return TokenService._create_token(data, expires, "refresh")
    
    @staticmethod
    def verify_and_decode_token(token: str, expected_type: str) -> Dict[str, Any]:
        """
        The single function to be used for all token verification.
        It decodes the token, validates its signature and expiration,
        and crucially, verifies its type ('access' or 'refresh').
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            token_type = payload.get("type")
            if token_type != expected_type:
                raise jwt.InvalidTokenError(f"Invalid token type: expected '{expected_type}', got '{token_type}'")
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError("Token has expired")
        except jwt.PyJWTError as e:
            # Catches all other JWT errors (invalid signature, malformed, etc.)
            raise jwt.InvalidTokenError(f"Invalid token: {e}")
        

    @staticmethod
    async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: AsyncSession = Depends(get_db)) -> User:
        '''Get the current user from the token'''
        token = creds.credentials
        payload = TokenService.verify_token(token)
        user_id = int(payload.get("sub"))
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user