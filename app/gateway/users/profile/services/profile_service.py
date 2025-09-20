from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from app.gateway.users.user.models.users import User
from app.gateway.users.profile.schemas.profile_schemas import UserUpdate, UserProfileResponse, SimpleEnterpriseResponse, SimpleStaffEnterpriseResponse
from app.gateway.auth.services.auth_service import AuthService, PasswordPolicy
from app.gateway.enterprises.models.enterprises import Enterprise, Staff, Client
from fastapi import HTTPException, status
from typing import Optional

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

    async def update_user_profile(self, user_id: int, user_data: UserUpdate) -> tuple[User | None, str]:
        """Update user profile and ensure unique constraints are not violated"""
        
        # Ensure data is valid and iterable        
        update_data = user_data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided for update")
        
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

        # Update user fields only if provided (partial update)
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.username is not None:
            user.username = user_data.username
        if user_data.first_name is not None:
            user.first_name = user_data.first_name
        if user_data.last_name is not None:
            user.last_name = user_data.last_name
        if user_data.phone_number is not None:
            user.phone_number = user_data.phone_number

        await self.session.commit()
        return user, ''

    async def get_user_profile(self, user_id: int) -> Optional[UserProfileResponse]:
        """Get complete user profile including enterprise relationships"""
        
        # Get user with all enterprise relationships
        stmt = select(User).options(
            selectinload(User.enterprises).options(
                selectinload(Enterprise.staffs),
                selectinload(Enterprise.clients)
            ),
            selectinload(User.staff_profiles).options(
                selectinload(Staff.enterprise)
            )
        ).filter(User.id == user_id)
        
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None

        # Build owned enterprises data (simplified)
        owned_enterprises = []
        for enterprise in user.enterprises:
            owned_enterprises.append(SimpleEnterpriseResponse(
                id=enterprise.id,
                name=enterprise.name,
                type=enterprise.type
            ))

        # Build staff enterprises data (simplified)
        staff_enterprises = []
        for staff_profile in user.staff_profiles:
            if staff_profile.is_active:
                enterprise = staff_profile.enterprise
                staff_enterprises.append(SimpleStaffEnterpriseResponse(
                    id=enterprise.id,
                    name=enterprise.name,
                    type=enterprise.type,
                    role=staff_profile.role
                ))

        return UserProfileResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            subscription_plan=user.subscription_plan.value,
            is_active=user.is_active,
            email_verified=user.email_verified,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            last_login=user.last_login,
            owned_enterprises=owned_enterprises,
            staff_enterprises=staff_enterprises
        )