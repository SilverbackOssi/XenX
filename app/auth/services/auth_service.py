from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.auth.models.user import User, UserRole
from typing import Optional
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
