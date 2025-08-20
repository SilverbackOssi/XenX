from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database import get_db
from app.auth.schemas.auth_schemas import ForgotPasswordSchema, LoginWithCodeSchema, ResetPasswordSchema
from app.auth.services.auth_service import AuthService
from app.auth.services.email_service import EmailService


email_service = EmailService()
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(payload: ForgotPasswordSchema, db: AsyncSession = Depends(get_db)):
    """
    Forgot password endpoint.
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    otp_code = await auth_service.create_otp(user)
    await email_service.send_login_code_email(payload.email, otp_code)
    return {"message": "A code has been sent to your email."}

@auth_router.post("/login-with-code", status_code=status.HTTP_200_OK)
async def login_with_code(payload: LoginWithCodeSchema, db: AsyncSession = Depends(get_db)):
    """
    Login with one-time code endpoint.
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not await auth_service.verify_otp(user, payload.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code",
        )

    await auth_service.clear_otp(user)
    return await auth_service.login_with_code(user.email)

@auth_router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(payload: ResetPasswordSchema, db: AsyncSession = Depends(get_db)):
    """
    Reset password endpoint.
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not await auth_service.verify_otp(user, payload.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code",
        )

    user.password_hash = auth_service.get_password_hash(payload.new_password)  # type: ignore
    await auth_service.clear_otp(user)
    await db.commit()

    return {"message": "Password reset successful."}