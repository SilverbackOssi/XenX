from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.auth.models.users import User
from app.auth.services.token_service import TokenService
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
import re
import secrets
import string
from app.auth.services.email_service import EmailService
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordPolicy:
    MIN_LENGTH = 8
    # Define allowed special characters in one place for easier maintenance.
    ALLOWED_SPECIAL_CHARS = "@$!%*?&"
    
    # Build the pattern dynamically for clarity and to avoid repetition.
    # re.escape is used to ensure characters are treated as literals in the regex.
    PATTERN = re.compile(
        r'^(?=.*[a-z])'
        r'(?=.*[A-Z])'
        r'(?=.*\d)'
        rf'(?=.*[{re.escape(ALLOWED_SPECIAL_CHARS)}])'
        rf'[A-Za-z\d{re.escape(ALLOWED_SPECIAL_CHARS)}]+$'
    )

    @classmethod
    def validate(cls, password: str) -> tuple[bool, str]:
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters long"
        if not cls.PATTERN.match(password):
            return False, f"Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character from the set: {cls.ALLOWED_SPECIAL_CHARS}"
        return True, ""

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # Password confirmation
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    # Create user from google
    async def create_user_from_google(
        self,
        email: str,
        username: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> tuple[User | None, str]:
        # Generate a random password that user won't use (for OAuth users)
        def generate_strong_password(length=16):
            special_chars = "@$!%*?&"
            alphabet = string.ascii_letters + string.digits + special_chars
            while True:
                password = ''.join(secrets.choice(alphabet) for _ in range(length))
                if (any(c.islower() for c in password) and
                    any(c.isupper() for c in password) and
                    any(c.isdigit() for c in password) and
                    any(c in special_chars for c in password)):
                    return password

        random_password = generate_strong_password()

        user = User(
                email=email,
                username=username,
                password_hash=self.get_password_hash(random_password),
                first_name=first_name,
                last_name=last_name,
                phone_number=None,
                )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user, ""

    # Create user
    async def create_user(
        self, 
        email: str, 
        username: str, 
        password: str, 
        # role: UserRole,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> tuple[User | None, str]:
        # Validate password
        is_valid, error_msg = PasswordPolicy.validate(password)
        if not is_valid:
            return None, error_msg

        try:
            verification_token = secrets.token_urlsafe(32)
            verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

            user = User(
                email=email,
                username=username,
                password_hash=self.get_password_hash(password),
                # role=role,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                verification_token=verification_token,
                verification_token_expires_at=verification_token_expires_at
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

            try:
                # Send verification email
                email_service = EmailService()
                verification_link = f"http://xenx.onrender.com/verify-email?token={verification_token}"
                await email_service.send_verification_email(email, verification_link)
            except Exception as e:
                await self.session.rollback()
                return user, f"User Created. Failed to send verification email: {str(e)}"

            return user, ""
        except IntegrityError as e:
            await self.session.rollback()
            if "users_email_key" in str(e):
                return None, "Email already registered"
            if "users_username_key" in str(e):
                return None, "Username already taken"
            return None, "Registration failed, user exists"
        except Exception as e:
            await self.session.rollback()
            return None, str(e)

    async def verify_user_email(self, token: str) -> tuple[bool, Union[str, Dict[str, Any]]]:
        result = await self.session.execute(select(User).filter(User.verification_token == token))
        user = result.scalar_one_or_none()

        if not user:
            return False, "Invalid verification token"

        if user.verification_token_expires_at < datetime.utcnow(): # type:ignore
            return False, "Verification token has expired"

        user.email_verified = True # type: ignore
        user.verification_token = None # type: ignore
        user.verification_token_expires_at = None # type: ignore
        await self.session.commit()

        # Send welcome email
        email_service = EmailService()
        await email_service.send_welcome_email(user.email) # type: ignore

        # Generate tokens
        tokens = TokenService.create_tokens_for_user(user)
        return True, tokens

    # Log user in
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
            
        if not bool(user.is_active):
            return None, "Account disabled"
            
        if not self.verify_password(password, user.password_hash): # type: ignore
            return None, "Invalid credentials"
            
        # Update last login time
        user.last_login = datetime.now(timezone.utc)  # type: ignore
        await self.session.commit()
        
        return user, ""
        
    async def login(self, email: Optional[str] = None, username: Optional[str] = None, password: str = None) -> Dict[str, Any]:
        if email:
            user = await self.get_user_by_email(email)
        elif username:
            user = await self.get_user_by_username(username)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username required")

        if not user or not self.verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

        # Increment token version to invalidate all old tokens
        user.token_version += 1
        await self.session.commit()
        await self.session.refresh(user)

        token_data = {
            "id": user.id, 
            "role": user.role, 
            "ver": user.token_version # Embed version in token
        }
        access_token = TokenService.create_access_token(data=token_data)
        refresh_token = TokenService.create_refresh_token(data=token_data)

        return {
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "token_type": "bearer",
            "user": user
        }
    
       
        
        # return {**tokens, "user": user_data}
    
    async def logout(self, user: User) -> None:
        """
        Logs out the user by invalidating all their current tokens.
        This is achieved by incrementing the user's token_version.

        Note: This is global logout. To implement single-device logout,
        I'd need to use redis blacklisting.
        """
        user.token_version += 1
        await self.session.commit()

    async def login_with_code(self, email: str) -> Dict[str, Any]:
        """Login a user with one-time code and return tokens"""
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account disabled"
            )

        # Update last login time
        user.last_login = datetime.now(timezone.utc)
        await self.session.commit()

        # Generate tokens
        tokens = TokenService.create_tokens_for_user(user)

        # Add user info to response
        user_data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            # "role": user.role.value,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "email_verified": user.email_verified
        }

        return {**tokens, "user": user_data}
        
    async def create_otp(self, user: User) -> str:
        """Generate and save OTP for a user"""
        otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        user.otp_code = self.get_password_hash(otp) # Hash the OTP
        user.otp_code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10) # OTP valid for 10 minutes
        await self.session.commit()
        return otp

    async def verify_otp(self, user: User, otp: str) -> bool:
        """Verify OTP for a user"""
        if not user.otp_code or not user.otp_code_expires_at:
            return False
        if datetime.now(timezone.utc) > user.otp_code_expires_at:
            return False # OTP expired
        return self.verify_password(otp, user.otp_code)

    async def clear_otp(self, user: User):
        """Clear OTP for a user after use"""
        user.otp_code = None
        user.otp_code_expires_at = None
        await self.session.commit()
        
    async def update_password(self, user_id: int, new_password: str) -> bool:
        """Update a user's password after account recovery
        
        Args:
            user_id: The ID of the user
            new_password: The new password to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate password first
            is_valid, error_msg = PasswordPolicy.validate(new_password)
            if not is_valid:
                raise ValueError(error_msg)
                
            # Get the user
            user = await self.session.get(User, user_id)
            if not user:
                return False
                
            # Update the password
            hashed_password = self.get_password_hash(new_password)
            user.password_hash = hashed_password
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False

    # New access token
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Generate new access token using refresh token"""
        try:
            # Verify the refresh token
            payload = TokenService.verify_and_decode_token(refresh_token, expected_type="refresh")
            user_id = payload.get("id")
            token_ver = payload.get("ver")

            if user_id is None or token_ver is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
            
            user = await self.session.get(User, user_id)
            if not user or user.token_version != token_ver:
                # This is a security event: an old token was used.
                # You could add logging here to flag potential token theft.
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

            # Increment version for rotation
            user.token_version += 1
            await self.session.commit()
            await self.session.refresh(user)

            new_token_data = {
                "id": user.id, 
                "role": user.role, 
                "ver": user.token_version
            }
            new_access_token = TokenService.create_access_token(data=new_token_data)
            
            return {"access_token": new_access_token, "token_type": "bearer"}
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        except TokenService.jwt.InvalidTokenError as e: # Catch the specific error
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


        #     # Get the user
        #     result = await self.session.execute(select(User).filter(User.id == user_id))
        #     user = result.scalar_one_or_none()