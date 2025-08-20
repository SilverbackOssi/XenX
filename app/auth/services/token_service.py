from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from fastapi import Depends, HTTPException, status
from app.auth.models.users import User
from app.auth.database import get_db

# These should be in environment variables in production
SECRET_KEY = "secret-key-for-jwt-tokens"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class TokenService:
    @staticmethod
    def create_access_token(user_id: int) -> str:
        """Create a new access token for a user"""
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(timezone.utc) + expires_delta
        
        to_encode = {
            "sub": str(user_id),
            # "role": role.value,
            "exp": expire.timestamp(),
            "type": "access"
        }
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Create a new refresh token for a user"""
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.now(timezone.utc) + expires_delta
        
        to_encode = {
            "sub": str(user_id),
            # "role": role.value,
            "exp": expire.timestamp(),
            "type": "refresh"
        }
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> dict:
        """Verify a token is valid and not expired"""
        payload = TokenService.decode_token(token)
        
        # Check token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    @staticmethod
    def create_tokens_for_user(user: User) -> Dict[str, str]:
        """Create both access and refresh tokens for a user"""
        access_token = TokenService.create_access_token(user.id)
        refresh_token = TokenService.create_refresh_token(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
        '''Get the current user from the token'''
        payload = TokenService.verify_token(token)
        user_id = int(payload.get("sub"))
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user