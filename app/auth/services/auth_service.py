from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.auth.models.users import User, UserRole
from app.auth.services.token_service import TokenService
from typing import Optional, Dict, Any, Union
from datetime import datetime
from fastapi import HTTPException, status
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordPolicy:
    MIN_LENGTH = 8
    PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$')

    @classmethod
    def validate(cls, password: str) -> tuple[bool, str]:
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters long"
        if not cls.PATTERN.match(password):
            return False, "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
        return True, ""

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def create_user(
        self, 
        email: str, 
        username: str, 
        password: str, 
        role: UserRole,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> tuple[User | None, str]:
        # Validate password
        is_valid, error_msg = PasswordPolicy.validate(password)
        if not is_valid:
            return None, error_msg

        try:
            user = User(
                email=email,
                username=username,
                password_hash=self.get_password_hash(password),
                role=role,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user, ""
        except IntegrityError as e:
            await self.session.rollback()
            if "users_email_key" in str(e):
                return None, "Email already registered"
            if "users_username_key" in str(e):
                return None, "Username already taken"
            return None, "Registration failed, integrity error"
        except Exception as e:
            await self.session.rollback()
            return None, str(e)

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()
        
    async def authenticate_user(self, login_id: str, password: str, is_email: bool = True) -> tuple[User | None, str]:
        """Authenticate a user by email/username and password"""
        if is_email:
            user = await self.get_user_by_email(login_id)
        else:
            user = await self.get_user_by_username(login_id)
            
        if not user:
            return None, "Invalid credentials"
            
        if not user.is_active:
            return None, "Account disabled"
            
        if not self.verify_password(password, user.password_hash):
            return None, "Invalid credentials"
            
        # Update last login time
        user.last_login = datetime.utcnow()
        await self.session.commit()
        
        return user, ""
        
    async def login(self, email: Optional[str] = None, username: Optional[str] = None, password: str = None) -> Dict[str, Any]:
        """Login a user and return tokens"""
        if email:
            user, error = await self.authenticate_user(email, password, is_email=True)
        elif username:
            user, error = await self.authenticate_user(username, password, is_email=False)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either email or username must be provided"
            )
            
        if error:
            status_code = status.HTTP_401_UNAUTHORIZED
            if error == "Account disabled":
                status_code = status.HTTP_403_FORBIDDEN
                
            raise HTTPException(
                status_code=status_code,
                detail=error,
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Generate tokens
        tokens = TokenService.create_tokens_for_user(user)
        
        # Add user info to response
        user_data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "email_verified": user.email_verified
        }
        
        return {**tokens, "user": user_data}
        
    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Generate new access token using refresh token"""
        try:
            # Verify the refresh token
            payload = TokenService.verify_token(refresh_token, token_type="refresh")
            user_id = int(payload.get("sub"))
            
            # Get the user
            result = await self.session.execute(select(User).filter(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            # Generate new tokens
            return TokenService.create_tokens_for_user(user)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"}
            )
