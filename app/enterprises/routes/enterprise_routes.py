import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database import get_db
from app.auth.services.token_service import TokenService
from app.auth.models.users import User
from app.enterprises.schemas.enterprise_schemas import EnterpriseCreate, EnterpriseResponse
from app.enterprises.services.enterprise_service import EnterpriseService
from app.auth.services.auth_service import AuthService
from app.enterprises.schemas.staff_schemas import StaffInvitation, MultipleStaffInvitations
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
load_dotenv()

enterprise_router = APIRouter(prefix="/enterprises", tags=["Enterprises"])

@enterprise_router.post("/create", response_model=EnterpriseResponse, status_code=status.HTTP_201_CREATED)
async def create_enterprise(
    enterprise_data: EnterpriseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
) -> EnterpriseResponse:
    """
    Create a new firm for the current user.
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

# XXX Should also return associated users(owner, staff, and clients)
# @enterprise_router.get("/{enterprise_id}", response_model=EnterpriseResponse, status_code=status.HTTP_200_OK)
# async def get_enterprise(
#     enterprise_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(TokenService.get_current_user)
# ) -> EnterpriseResponse:
#     """
#     Get details of a specific firm.
#     Requires permission
#     """
#     enterprise_service = EnterpriseService(db)
#     enterprise, error = await enterprise_service.get_enterprise(
#         user_id=current_user.id,  # type: ignore
#         enterprise_id=enterprise_id
#     )
#     if error:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=error
#         )
#     return enterprise

@enterprise_router.post("/{enterprise_id}/invite", status_code=status.HTTP_200_OK, summary="Invite an assistant")
async def invite_assistant_to_enterprise(
    enterprise_id: int,
    invitation_data: StaffInvitation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Invite a single teammate to a firm.
    """
    enterprise_service = EnterpriseService(db)
    auth_service = AuthService(db)
    otp = secrets.token_hex(4)  # Generate a random 4-byte OTP
            
    staff, error = await enterprise_service.invite_teammate(
        enterprise_id=enterprise_id,
        inviter=current_user,
        invitation_data=invitation_data,
        hashed_otp=auth_service.get_password_hash(otp)  # Set the OTP as the user's password
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
    """
    enterprise_service = EnterpriseService(db)
    auth_service = AuthService(db)
    
    result, error = await enterprise_service.invite_multiple_teammates(
        enterprise_id=enterprise_id,
        inviter=current_user,
        invitations=invitation_data.invitations,
        auth_service=auth_service
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
    enterprise_service = EnterpriseService(db)
    staff, error = await enterprise_service.accept_invitation(
        token=token
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    # Redirect to frontend login page after successful acceptance
    
    frontend_url = os.getenv("FRONTEND_LOGIN_URL", "https://xentoba.pxxl.pro/login")
    return RedirectResponse(url=frontend_url, status_code=status.HTTP_302_FOUND)
