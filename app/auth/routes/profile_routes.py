

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database import get_db
from app.schemas.schema import UserResponse
from app.auth.schemas.profile_schemas import ChangePasswordRequest
from app.auth.models.users import User
from app.auth.services.profile_service import ProfileService
from app.auth.services.token_service import TokenService


profile_router = APIRouter(prefix="/users", tags=["User Profile"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    payload = TokenService.verify_token(token)
    user_id = int(payload.get("sub"))
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@profile_router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user

@profile_router.put("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile_service = ProfileService(db)
    await profile_service.change_password(
        user_id=current_user.id, # type: ignore
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    return

@profile_router.get("/me/subscription")
async def get_user_subscription(current_user: User = Depends(get_current_user)):
    return {"subscription_plan": current_user.subscription_plan}
