

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.gateway.auth.database import get_db
from app.gateway.users.user.schemas.user_schemas import UserResponse
from ..schemas.profile_schemas import ChangePasswordRequest, UserProfileResponse, UserUpdate
from app.gateway.users.user.models.users import User
from ..services.profile_service import ProfileService
from ....auth.services.token_service import TokenService


profile_router = APIRouter(prefix="/users", tags=["Users"])


@profile_router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(TokenService.get_current_user)) -> User:
    return current_user

@profile_router.get("/me/profile", response_model=UserProfileResponse)
async def get_complete_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """Get complete user profile including enterprise relationships"""
    profile_service = ProfileService(db)
    profile = await profile_service.get_user_profile(current_user.id)  # type: ignore
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

@profile_router.patch("/me", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    profile_service = ProfileService(db)
    updated_user, error = await profile_service.update_user_profile(
        user_id=current_user.id,  # type: ignore
        user_data=user_data
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    return updated_user


@profile_router.put("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    profile_service = ProfileService(db)
    await profile_service.change_password(
        user_id=current_user.id, # type: ignore
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    return

@profile_router.get("/me/subscription")
async def get_user_subscription(current_user: User = Depends(TokenService.get_current_user)):
    return {"subscription_plan": current_user.subscription_plan}
