from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.auth.models.users import User
from app.auth.schemas.profile_schemas import UserUpdate
from app.auth.services.auth_service import AuthService, PasswordPolicy
from fastapi import HTTPException, status

class ProfileService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.auth_service = AuthService(session)

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        """Change user's password"""
        # Get user
        result = await self.session.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Verify old password
        if not self.auth_service.verify_password(old_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")

        # Validate new password
        is_valid, error_msg = PasswordPolicy.validate(new_password)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        # Hash and update new password
        user.password_hash = self.auth_service.get_password_hash(new_password)
        await self.session.commit()

    async def update_user_profile(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user profile and ensure unique constraints are not violated"""
        result = await self.session.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Check for unique email
        if user_data.email and user_data.email != user.email:
            email_check = await self.session.execute(
                select(User).filter(User.email == user_data.email, User.id != user_id)
            )
            if email_check.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

        # Check for unique username
        if user_data.username and user_data.username != user.username:
            username_check = await self.session.execute(
                select(User).filter(User.username == user_data.username, User.id != user_id)
            )
            if username_check.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in use")

        # Update user fields
        user.email = user_data.email
        user.username = user_data.username
        user.first_name = user_data.first_name
        user.last_name = user_data.last_name
        user.phone_number = user_data.phone_number

        await self.session.commit()
        return user