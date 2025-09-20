
    
from typing import Optional, Tuple   
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select    
from app.gateway.users.user.models.users import User
from ..models.enterprises import Enterprise, Staff, StaffPermission

class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def has_owner_permission(self, enterprise: Enterprise, user_id: int) -> bool:
        """
        Check if a user is owner or system admin.
        """
        try:
            # Check if user is a superuser
            user = await self.db.get(User, user_id)
            if user and getattr(user, "is_superuser", False):
                return True

            # Check if user is the owner
            if enterprise.owner_id == user_id: # type: ignore
                return True

            return False
        except Exception:
            return False

    async def has_full_access(self, enterprise: Enterprise, user_id: int) -> bool:
        """
        Check if a user has permission to update an enterprise.
        """
        try:
            if await self.has_owner_permission(enterprise, user_id):
                return True

            result = await self.db.execute(
                select(Staff).filter_by(
                    user_id=user_id,
                    enterprise_id=enterprise.id,
                    is_active=True
                )
            )
            staff = result.scalar_one_or_none() 

            if staff:
                if bool(staff.permission == StaffPermission.FULL_ACCESS):
                    return True
            return False
        except Exception:
            return False

    async def has_manage_access(self, enterprise: Enterprise, user_id: int) -> bool:
        """
        Check if a user has permission to manage an enterprise.
        """
        try:
            if await self.has_full_access(enterprise, user_id):
                return True

            result = await self.db.execute(
                select(Staff).filter_by(
                    user_id=user_id,
                    enterprise_id=enterprise.id,
                    is_active=True
                )
            )
            staff = result.scalar_one_or_none()

            if staff:
                if bool(staff.permission == StaffPermission.MANAGE):
                    return True
            return False
        except Exception:
            return False

    async def has_edit_access(self, enterprise: Enterprise, user_id: int) -> bool:
        """
        Check if a user has permission to edit an enterprise document.
        """
        try:
            if await self.has_manage_access(enterprise, user_id):
                return True

            result = await self.db.execute(
                select(Staff).filter_by(
                    user_id=user_id,
                    enterprise_id=enterprise.id,
                    is_active=True
                )
            )
            staff = result.scalar_one_or_none()

            if staff:
                if bool(staff.permission == StaffPermission.EDIT):
                    return True
            return False
        except Exception:
            return False

    async def has_view_access(self, enterprise: Enterprise, user_id: int) -> bool:
        try:
            if await self.has_edit_access(enterprise, user_id):
                return True

            result = await self.db.execute(
                select(Staff).filter_by(
                    user_id=user_id,
                    enterprise_id=enterprise.id,
                    is_active=True
                )
            )
            staff = result.scalar_one_or_none()

            if staff:
                if bool(staff.permission == StaffPermission.VIEW_ONLY):
                    return True
            return False
        except Exception:
            return False

    async def update_staff_permissions(self,
        enterprise: Enterprise,
        staff_id: int,
        permission: StaffPermission,
        current_user: User
    ) -> Tuple[Optional[Staff], Optional[str]]:
        try:
            # Check if the current user has permission to update staff permissions
            if not await self.has_full_access(enterprise, current_user.id):
                return None, "User does not have permission to update staff permissions"

            staff = await self.db.get(Staff, staff_id)
            if not staff:
                return None, "Staff not found"

            staff.permission = permission
            await self.db.commit()
            await self.db.refresh(staff)

            return staff, None
        except Exception as e:
            return None, str(e)
