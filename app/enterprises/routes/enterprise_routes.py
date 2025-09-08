from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse

from app.auth.database import get_db
from app.auth.models.users import User
from app.auth.dependencies import get_current_user
from app.enterprises.dependencies import require_permission
from app.enterprises.models.enterprises import Enterprise
from app.enterprises.schemas.enterprise_schemas import EnterpriseCreate, EnterpriseResponse
from app.enterprises.schemas.staff_schemas import StaffInvitation, MultipleStaffInvitations
from app.enterprises.services.enterprise_service import EnterpriseService
from app.config import get_settings


settings = get_settings()

enterprise_router = APIRouter(
    prefix="/enterprises",
    tags=["Enterprises"]
)

@enterprise_router.post("/create", response_model=EnterpriseResponse, status_code=status.HTTP_201_CREATED)
async def create_enterprise(
    enterprise_data: EnterpriseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> EnterpriseResponse:
    """
    Create a new enterprise for the current user.
    """
    enterprise_service = EnterpriseService(db)
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

@enterprise_router.get(
        "/{enterprise_id}", 
        response_model=EnterpriseResponse,
        summary="Get enterprise details by IFD",
        status_code=status.HTTP_200_OK
)
async def get_enterprise(
    # enterprise_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(TokenService.get_current_user)
    enterprise: Enterprise = Depends(require_permission("view")),
) -> EnterpriseResponse:
    """
    Get details of a specific enterprise.
    Access is restricted to users with at least VIEW permission.
    """
    # The dependency already verified permission and fetched the enterprise.
    # We just need to load relationships for the response model.
    await db.refresh(enterprise, ["staffs", "clients"])
    
    response_data = EnterpriseResponse.model_validate(enterprise)
    # Manually populate IDs from the refreshed relationships
    response_data.staff_ids = [staff.id for staff in enterprise.staffs]
    response_data.client_ids = [client.id for client in enterprise.clients]
    
    return response_data
    
    
    # Convert the enterprise to a dict for modification
    # enterprise_dict = {
    #     **{c.name: getattr(enterprise, c.name) for c in enterprise.__table__.columns},
    #     "staff_ids": [staff.id for staff in getattr(enterprise, "staffs", [])] if hasattr(enterprise, "staffs") and enterprise.staffs else [],
    #     "client_ids": [client.id for client in getattr(enterprise, "clients", [])] if hasattr(enterprise, "clients") and enterprise.clients else []
    # }
    
    # Create the response model from the modified dict using the newer model_validate method
    # return EnterpriseResponse.model_validate(enterprise_dict)

@enterprise_router.post("/{enterprise_id}/invite", status_code=status.HTTP_200_OK, summary="Invite an assistant")
async def invite_assistant_to_enterprise(
    invitation_data: StaffInvitation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    enterprise: Enterprise = Depends(require_permission("manage"))
):
    """
    Invite a single teammate to a firm.
    Requires at least MANAGE permission.
    """
    enterprise_service = EnterpriseService(db)
    _, error = await enterprise_service.invite_teammate(
        enterprise_id=enterprise.id, # type: ignore
        inviter=current_user,
        invitation_data=invitation_data
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {"message": "Invitation sent successfully"}

@enterprise_router.post("/{enterprise_id}/invite-multiple", status_code=status.HTTP_200_OK, summary="Invite multiple assistants")
async def invite_multiple_assistants_to_enterprise(
    invitation_data: MultipleStaffInvitations,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    enterprise: Enterprise = Depends(require_permission("manage"))
):
    """
    Invite multiple teammates to a firm in a single request.
    Requires at least MANAGE permission.
    """
    enterprise_service = EnterpriseService(db)
    
    # Check permissions
    result, error = await enterprise_service.invite_multiple_teammates(
        enterprise_id=enterprise.id,
        inviter=current_user,
        invitations=invitation_data.invitations
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    return {
        "message": f"Processed {len(invitation_data.invitations)} invitation(s)",
        "successful": len(result.get("successful", [])) if result else 0,
        "failed": result.get("failed", []) if result else []
    }

@enterprise_router.get("/accept-invite", status_code=status.HTTP_200_OK, summary="Accept an invitation")
async def accept_invitation(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Accept an invitation to join a firm.
    Redirects to the frontend login page on success.
    """
    enterprise_service = EnterpriseService(db)
    _, error = await enterprise_service.accept_invitation(
        token=token
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    # Redirect to frontend login page after successful acceptance
    
    frontend_url = settings.FRONTEND_LOGIN_URL
    return RedirectResponse(url=frontend_url, status_code=status.HTTP_302_FOUND)

