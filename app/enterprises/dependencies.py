from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable

from app.auth.dependencies import get_current_user
from app.auth.models.users import User
from app.auth.database import get_db
from app.enterprises.models.enterprises import Enterprise
from app.enterprises.services.enterprise_service import EnterpriseService
from app.enterprises.services.permission_service import PermissionService

def require_permission(level: str) -> Callable:
    """
    Dependency factory. Creates a dependency that requires a specific permission level
    ('view' or 'manage') for an enterprise.

    This fetches the enterprise, checks the current user's permission,
    and returns the enterprise object if successful.
    """
    async def _verify_permission(
        enterprise_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> Enterprise:
        
        enterprise_service = EnterpriseService(db)
        permission_service = PermissionService(db)

        # 1. Fetch the enterprise
        enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
        if error or not enterprise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enterprise not found")

        # 2. Check permission based on the required level
        has_access = False
        user_id = current_user.id 
        
        if level == "view":
            has_access = await permission_service.has_view_access(enterprise, user_id)
        elif level == "manage":
            has_access = await permission_service.has_manage_access(enterprise, user_id)
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have '{level}' permission for this enterprise."
            )
        
        # 3. Return the enterprise object for use in the endpoint
        return enterprise

    return _verify_permission

# async def get_enterprise_by_id(enterprise_id: int, db: AsyncSession = Depends(get_db)) -> Enterprise:
#     """Dependency to fetch an enterprise by its ID."""
#     enterprise = await db.get(Enterprise, enterprise_id)
#     if not enterprise:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enterprise not found")
#     return enterprise

# def verify_enterprise_membership(
#     current_user: User = Depends(get_current_user),
#     enterprise: Enterprise = Depends(get_enterprise_by_id)
# ):
#     """
#     Dependency that verifies if the current user is part of the enterprise
#     they are trying to access.
#     """
#     if current_user.enterprise_id != enterprise.id:
#         # Admins are a special case; they can access any enterprise.
#         if current_user.role != "admin":
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="You do not have permission to access this enterprise's resources."
#             )
#     return enterprise

