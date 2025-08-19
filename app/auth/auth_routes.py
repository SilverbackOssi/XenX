from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database import get_db
from app.schemas.schema import UserCreate, UserResponse
from app.auth.schemas.auth_schemas import LoginRequest, TokenResponse, RefreshRequest, LoginResponse
from app.auth.services.auth_service import AuthService
from app.auth.services.email_service import EmailService
from typing import Dict, Any


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    user, error = await auth_service.create_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        # role=user_data.role,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number
    )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return user

@auth_router.get("/verify-email/{token}", status_code=status.HTTP_200_OK)
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
    return result


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

