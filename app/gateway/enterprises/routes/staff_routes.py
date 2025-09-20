from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.gateway.auth.database import get_db
from app.gateway.users.user.models.users import User
from app.gateway.auth.services.token_service import TokenService
from ..models.enterprises import Enterprise
from ..models.permissions import StaffPermission
from ..schemas.staff_schemas import StaffPermissionUpdate, StaffResponse
from ..services.enterprise_service import EnterpriseService
from ..services.permission_service import PermissionService


staff_router = APIRouter(prefix="/enterprises", tags=["Enterprise Staffs"])

# STAFFS
@staff_router.get("/{enterprise_id}/staffs", response_model=List[StaffResponse], status_code=status.HTTP_200_OK)
async def get_all_staffs(
    enterprise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Get all staff members of an enterprise.
    Requires VIEW permission.
    Returns list of staff members with their details, including invited staff and client IDs.
    """
    enterprise_service = EnterpriseService(db)
    permission_service = PermissionService(db)

    # Get enterprise and check if it exists
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )

    # Check if user has permission to view this enterprise
    if not await permission_service.has_view_access(enterprise, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this enterprise"
        )

    # Get all staff members
    staffs, error = await enterprise_service.get_all_staffs(enterprise_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    # Return empty array if no staffs found
    if not staffs:
        return []
        
    return staffs

@staff_router.get("/{enterprise_id}/staffs/{staff_id}", response_model=StaffResponse, status_code=status.HTTP_200_OK)
async def get_staff_profile(
    enterprise_id: int,
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Get staff profile information.
    Requires VIEW permission
    """
    enterprise_service = EnterpriseService(db)
    permission_service = PermissionService(db)
    
    # Get enterprise and check if it exists
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )
    
    # Check if user has permission to view this enterprise
    if not await permission_service.has_view_access(enterprise, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this enterprise"
        )
    
    # Get staff details with invited staff and clients
    staff, error = await enterprise_service.get_staff_by_id(enterprise_id, staff_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    return staff

#  PERMISSIONS
@staff_router.put("/{enterprise_id}/staffs/{staff_id}/permissions", response_model=StaffPermissionUpdate, status_code=status.HTTP_200_OK)
async def update_staff_permission(
    enterprise_id: int,
    staff_id: int,
    permission: StaffPermission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Update user permissions in an enterprise.
    Only the owner or a staff member with FULL permission can update permissions.
    """
    permission_service = PermissionService(db)
    enterprise_service = EnterpriseService(db)
    
    # Get enterprise and check if it exists
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )
    
    # Check if user has permission to manage this enterprise
    if not await permission_service.has_full_access(enterprise, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage staff in this enterprise"
        )
    
    # Update staff permissions
    updated_staff, error = await permission_service.update_staff_permissions(
        enterprise=enterprise,
        staff_id=staff_id,
        permission=permission,
        current_user=current_user
    )

    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return updated_staff


# CLIENTS
client_router = APIRouter(prefix="/enterprises", tags=["Enterprise Clients"])
@client_router.get("/{enterprise_id}/clients", response_model=List[StaffResponse], status_code=status.HTTP_200_OK)
async def get_all_clients(
    enterprise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Get all clients of an enterprise.
    Requires VIEW permission.
    Returns list of clients with their details.
    """
    enterprise_service = EnterpriseService(db)
    permission_service = PermissionService(db)

    # Get enterprise and check if it exists
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )

    # Check if user has permission to view this enterprise
    if not await permission_service.has_view_access(enterprise, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this enterprise"
        )

    # Get all clients
    clients, error = await enterprise_service.get_all_clients(enterprise_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    # Return empty array if no clients found
    if not clients:
        return []
        
    return clients

@client_router.get("/{enterprise_id}/clients/{client_id}", response_model=StaffResponse, status_code=status.HTTP_200_OK)
async def get_client_profile(
    enterprise_id: int,
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Get client profile information.
    Requires VIEW permission
    """
    enterprise_service = EnterpriseService(db)
    permission_service = PermissionService(db)
    
    # Get enterprise and check if it exists
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )
    
    # Check if user has permission to view this enterprise
    if not await permission_service.has_view_access(enterprise, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this enterprise"
        )
    
    # Get client details
    client, error = await enterprise_service.get_client_by_id(enterprise_id, client_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    return client