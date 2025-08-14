from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from redis import Redis
from typing import List

from app.auth.schemas.auth import (
    UserCreate, UserResponse, TokenResponse, RefreshToken,
    MFAEnrollResponse, PasswordReset, PasswordResetConfirm
)
from app.auth.services.auth_service import AuthService
from app.core.dependencies import get_db, get_redis, get_current_user
from app.auth.models.user import User
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Register a new user."""
    auth_service = AuthService(db, redis)
    user = auth_service.create_user(user_data)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    request: Request = None
):
    """Authenticate user and return tokens."""
    auth_service = AuthService(db, redis)
    user = auth_service.authenticate_user(
        form_data.username,  # OAuth2 form uses username field for email
        form_data.password,
        form_data.scopes[0] if form_data.scopes else None  # Using scopes for MFA code
    )
    
    # Create audit log
    await create_audit_log(
        db=db,
        user=user,
        action="login",
        resource="auth",
        request=request
    )
    
    return auth_service.create_tokens(user)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: RefreshToken,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Use refresh token to get new access token."""
    auth_service = AuthService(db, redis)
    return auth_service.refresh_access_token(refresh_token.refresh_token)

@router.post("/logout")
async def logout(
    refresh_token: RefreshToken,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """Logout user and invalidate refresh token."""
    auth_service = AuthService(db, redis)
    auth_service.logout(refresh_token.refresh_token)
    return {"detail": "Successfully logged out"}

@router.post("/mfa/setup", response_model=MFAEnrollResponse)
async def setup_mfa(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """Setup MFA for current user."""
    auth_service = AuthService(db, redis)
    return auth_service.setup_mfa(current_user)

@router.post("/mfa/verify")
async def verify_mfa(
    code: str,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """Verify MFA code."""
    auth_service = AuthService(db, redis)
    if auth_service.verify_mfa_code(current_user, code):
        return {"detail": "MFA code verified"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid MFA code"
    )

@router.post("/password/reset", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    reset_data: PasswordReset,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Request password reset email."""
    auth_service = AuthService(db, redis)
    # Implementation would send reset email
    return {"detail": "If the email exists, a password reset link has been sent"}

@router.post("/password/reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Reset password using reset token."""
    auth_service = AuthService(db, redis)
    # Implementation would verify token and update password
    return {"detail": "Password has been reset"}

async def create_audit_log(
    db: Session,
    user: User,
    action: str,
    resource: str,
    request: Request
):
    """Create an audit log entry."""
    from app.auth.models.user import AuditLog
    
    audit_log = AuditLog(
        user_id=user.id,
        action=action,
        resource=resource,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    db.add(audit_log)
    db.commit()
