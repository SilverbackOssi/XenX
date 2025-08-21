import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database import get_db
from app.auth.services.token_service import TokenService
from app.auth.models.users import User
from app.enterprises.schemas.enterprise_schemas import EnterpriseCreate, EnterpriseResponse
from app.enterprises.services.enterprise_service import EnterpriseService
from app.auth.services.auth_service import AuthService
from app.enterprises.schemas.staff_schemas import StaffInvitation

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



@enterprise_router.post("/{enterprise_id}/invite", status_code=status.HTTP_200_OK)
async def invite_teammate_to_enterprise(
    enterprise_id: int,
    invitation_data: StaffInvitation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Invite a teammate to an enterprise.
    """
    enterprise_service = EnterpriseService(db)
    auth_service = AuthService(db)
    otp = secrets.token_hex(4)  # Generate a random 4-byte OTP
            
    staff, error = await enterprise_service.invite_teammate(
        enterprise_id=enterprise_id,
        inviter=current_user,
        invitation_data=invitation_data,
        otp=auth_service.get_password_hash(otp)  # Set the OTP as the user's password
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {"message": "Invitation sent successfully"}
