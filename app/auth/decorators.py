"""
Role-based access control decorators and utilities
"""
from functools import wraps
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.database import get_db
from app.auth.models.users import User, UserRole
from app.auth.services.token_service import TokenService


def require_roles(allowed_roles: List[UserRole]):
    """
    Decorator factory that creates a dependency for role-based access control.
    
    Args:
        allowed_roles: List of UserRole enums that are allowed to access the endpoint
        
    Returns:
        A FastAPI dependency function that validates user roles
        
    Example:
        @app.get("/admin/users")
        @require_roles([UserRole.ADMINISTRATOR])
        async def get_users(current_user: User = Depends(require_roles([UserRole.ADMINISTRATOR]))):
            ...
    """
    async def role_dependency(
        current_user: User = Depends(TokenService.get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    
    return role_dependency


def require_admin():
    """Convenience decorator for admin-only endpoints"""
    return require_roles([UserRole.ADMINISTRATOR])


def require_cpa_or_admin():
    """Convenience decorator for CPA or admin access"""
    return require_roles([UserRole.CPA, UserRole.ADMINISTRATOR])


def require_authenticated():
    """Basic authentication requirement (any valid user)"""
    return TokenService.get_current_user


# Role hierarchy for permission checking
ROLE_HIERARCHY = {
    UserRole.ADMINISTRATOR: 4,  # Highest privileges
    UserRole.CPA: 3,           # Can manage clients and staff
    UserRole.STAFF: 2,         # Limited organization access
    UserRole.CLIENT: 1,        # Basic user access
}


def has_permission(user_role: UserRole, required_role: UserRole) -> bool:
    """
    Check if a user role has sufficient permissions.
    Uses role hierarchy where higher-level roles inherit lower-level permissions.
    
    Args:
        user_role: The user's current role
        required_role: The minimum required role
        
    Returns:
        True if user has sufficient permissions
    """
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)


def check_resource_access(user: User, resource_owner_id: Optional[int] = None) -> bool:
    """
    Check if user can access a specific resource.
    
    Args:
        user: The current user
        resource_owner_id: ID of the user who owns the resource
        
    Returns:
        True if user can access the resource
    """
    # Administrators can access everything
    if user.role == UserRole.ADMINISTRATOR:
        return True
    
    # Users can always access their own resources
    if resource_owner_id and user.id == resource_owner_id:
        return True
    
    # CPAs can access resources in their organization (this would need organization context)
    if user.role == UserRole.CPA:
        # This would typically check organization membership
        # For now, return True as a placeholder
        return True
    
    return False