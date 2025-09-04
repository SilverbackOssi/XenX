from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database import get_db
from app.schemas.schema import UserCreate, UserResponse, UserRegisterResponse
from app.auth.schemas.auth_schemas import LoginRequest, TokenResponse, RefreshRequest, LoginResponse
from app.auth.services.auth_service import AuthService
from app.auth.services.email_service import EmailService
from typing import Dict, Any
from app.config import get_settings

from fastapi.responses import RedirectResponse

settings = get_settings()


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    user, error = await auth_service.create_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        role=user_data.role,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number
    )

    if error:
        if "user created" in error.lower():
            # Handle case where user is a dict (after rollback) or User object
            if isinstance(user, dict):
                response_data = {
                    "id": user["id"],
                    "email": user["email"],
                    "username": user["username"],
                    "subscription_plan": user["subscription_plan"].value if hasattr(user["subscription_plan"], 'value') else user["subscription_plan"],
                    "role": user["role"].value if hasattr(user["role"], 'value') else user["role"],
                    "last_name": user["last_name"],
                    "first_name": user["first_name"],
                    "phone_number": user["phone_number"],
                    "is_active": user["is_active"],
                    "email_verified": user["email_verified"],
                    "message": error
                }
            else:
                # User object case
                response_data = {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "subscription_plan": user.subscription_plan.value,
                    "role": user.role.value,
                    "last_name": user.last_name,
                    "first_name": user.first_name,
                    "phone_number": user.phone_number,
                    "is_active": user.is_active,
                    "email_verified": user.email_verified,
                    "message": error
                }
            return response_data
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

    # Create success response manually
    response_data = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "subscription_plan": user.subscription_plan.value,
        "role": user.role.value,
        "last_name": user.last_name,
        "first_name": user.first_name,
        "phone_number": user.phone_number,
        "is_active": user.is_active,
        "email_verified": user.email_verified,
        "message": "User successfully created, check your spam mail for verification mail"
    }
    return response_data

@auth_router.post("/resend-verification-email", status_code=status.HTTP_200_OK)
async def resend_verification_email(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    email_service = EmailService()
    user = await auth_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if bool(user.email_verified):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )
    
    token = user.verification_token
    verification_link = f"http://xenx.onrender.com/verify-email?token={token}"
    await email_service.send_verification_email(str(user.email), verification_link)
    
    return {"message": f"Verification email sent to {user.email}"}


@auth_router.get("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    success, result = await auth_service.verify_user_email(token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result
        )
    # return result    
    # Redirect to frontend login page after successful verification
    frontend_url = settings.FRONTEND_LOGIN_URL
    return RedirectResponse(url=frontend_url, status_code=status.HTTP_302_FOUND)


@auth_router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    auth_service = AuthService(db)
    return await auth_service.login(
        email=login_data.email,
        username=login_data.username,
        password=login_data.password
    )

@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    auth_service = AuthService(db)
    return await auth_service.refresh_token(refresh_data.refresh_token)
