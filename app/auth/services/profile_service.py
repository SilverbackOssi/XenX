from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.auth.models.users import User
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
