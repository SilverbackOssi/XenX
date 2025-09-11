from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database import get_db
from app.auth.services.token_service import TokenService
from app.auth.models.users import User
from app.enterprises.schemas.enterprise_schemas import TentantCreate, TentantResponse
from app.enterprises.services.enterprise_service import TentantService

from app.enterprises.schemas.staff_schemas import StaffInvitation, MultipleStaffInvitations
from fastapi.responses import RedirectResponse
from app.config import get_settings
from app.enterprises.services.permission_service import PermissionService

settings = get_settings()

enterprise_router = APIRouter(prefix="/enterprises", tags=["Enterprises"])

@enterprise_router.post("/create", response_model=TentantResponse, status_code=status.HTTP_201_CREATED)
async def create_enterprise(
    enterprise_data: TentantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
) -> TentantResponse:
    """
    Create a new firm for the current user.
    """
    enterprise_service = TentantService(db)
    enterprise, error = await enterprise_service.create_enterprise(
        user_id=current_user.id, # type: ignore
        enterprise_data=enterprise_data
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    return enterprise

@enterprise_router.get("/{enterprise_id}", response_model=TentantResponse, status_code=status.HTTP_200_OK)
async def get_enterprise(
    enterprise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
) -> TentantResponse:
    """
    Get details of a specific enterprise.
    Access is restricted to users with at least VIEW permission.
    Returns enterprise details along with associated staff IDs and client IDs.
    """
    enterprise_service = TentantService(db)
    permission_service = PermissionService(db)
    
    # Get enterprise with full relationships
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )
        
    # Check if user has at least view permission
    if not await permission_service.has_view_access(enterprise, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this enterprise"
        )
    
    # Ensure enterprise is not None before accessing attributes
    if enterprise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise not found"
        )
    
    # Explicitly load the staffs and clients relationships
    await db.refresh(enterprise, ["staffs", "clients"])
    
    # Convert the enterprise to a dict for modification
    enterprise_dict = {
        **{c.name: getattr(enterprise, c.name) for c in enterprise.__table__.columns},
        "staff_ids": [staff.id for staff in getattr(enterprise, "staffs", [])] if hasattr(enterprise, "staffs") and enterprise.staffs else [],
        "client_ids": [client.id for client in getattr(enterprise, "clients", [])] if hasattr(enterprise, "clients") and enterprise.clients else []
    }
    
    # Create the response model from the modified dict using the newer model_validate method
    return TentantResponse.model_validate(enterprise_dict)

@enterprise_router.post("/{enterprise_id}/invite", status_code=status.HTTP_200_OK, summary="Invite an assistant")
async def invite_assistant_to_enterprise(
    enterprise_id: int,
    invitation_data: StaffInvitation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Invite a single teammate to a firm.
    Requires at least MANAGE permission.
    """
    enterprise_service = TentantService(db)
    permission_service = PermissionService(db)

    # Check permissions
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)

    if not await permission_service.has_manage_access(enterprise, current_user.id):  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to invite users to this enterprise")

    staff, error = await enterprise_service.invite_teammate(
        enterprise_id=enterprise_id,
        inviter=current_user,
        invitation_data=invitation_data
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {"message": "Invitation sent successfully"}

@enterprise_router.post("/{enterprise_id}/invite-multiple", status_code=status.HTTP_200_OK, summary="Invite multiple assistants")
async def invite_multiple_assistants_to_enterprise(
    enterprise_id: int,
    invitation_data: MultipleStaffInvitations,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Invite multiple teammates to a firm in a single request.
    Requires at least MANAGE permission.
    """
    enterprise_service = TentantService(db)
    permission_service = PermissionService(db)
    

    # Check permissions
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)

    if not await permission_service.has_manage_access(enterprise, current_user.id):  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to invite users to this enterprise")

    result, error = await enterprise_service.invite_multiple_teammates(
        enterprise_id=enterprise_id,
        inviter=current_user,
        invitations=invitation_data.invitations
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
        
    # Return summary of successful and failed invitations
    return {
        "message": f"Processed {len(invitation_data.invitations)} invitation(s)",
        "successful": len(result.get("successful", [])) if result else 0,
        "failed": result.get("failed", []) if result else []
    }

@enterprise_router.get("/accept-invite", status_code=status.HTTP_200_OK)
async def accept_invitation(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Accept an invitation to join a firm.
    Redirects to the frontend login page on success.
    """
    enterprise_service = TentantService(db)
    staff, error = await enterprise_service.accept_invitation(
        token=token
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    # Redirect to frontend login page after successful acceptance
    
    frontend_url = settings.FRONTEND_LOGIN_URL
    return RedirectResponse(url=frontend_url, status_code=status.HTTP_302_FOUND)

