from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database import get_db
from app.auth.schemas.auth_schemas import (
    ForgotPasswordSchema, 
    LoginWithCodeSchema, 
    ResetPasswordSchema, 
    LoginCodeResponse,
    LoginResponse, 
    PasswordResetResponse,
    MessageResponse,
    AccountRecoveryRequest
)
from app.auth.services.auth_service import AuthService
from app.auth.services.email_service import EmailService


email_service = EmailService()
recovery_router = APIRouter(prefix="/auth", tags=["Account Recovery"])

@recovery_router.post(
    "/send-login-code", 
    status_code=status.HTTP_200_OK, 
    response_model=LoginCodeResponse,
    summary="Request a one-time login code"
)
async def send_one_time_login_code(payload: ForgotPasswordSchema, db: AsyncSession = Depends(get_db)):
    """
    Initiates the account recovery process by sending a one-time login code to the user's email.
    
    This endpoint should be used when:
    - A user has forgotten their password
    - A user wants to login without a password for security reasons
    
    The system will:
    1. Verify if the email exists in the database
    2. Generate a one-time password (OTP)
    3. Send the OTP to the user's email
    
    Returns a success message when the code is sent.
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(payload.email)
    
    # Always return the same message whether the email exists or not
    # This prevents user enumeration attacks
    response_message = {"message": "If your email is registered, you will receive a code shortly."}
    
    if user:
        try:
            otp_code = await auth_service.create_otp(user)
            await email_service.send_login_code_email(payload.email, otp_code)
        except Exception:
            # Silently fail to avoid leaking information about valid emails
            pass
            
    return response_message

@recovery_router.post(
    "/login-with-code", 
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    summary="Login using a one-time code"
)
async def login_with_code(payload: LoginWithCodeSchema, db: AsyncSession = Depends(get_db)):
    """
    Authenticates a user using their email and a one-time code sent to their email.
    
    This endpoint allows users to:
    - Log in without using their password
    - Access their account after requesting a one-time code
    - Begin the account recovery process
    
    The system will:
    1. Verify the user exists
    2. Validate the provided one-time code
    3. Generate access and refresh tokens
    4. Clear the used one-time code
    
    Returns authentication tokens and user information upon successful verification.
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address",
        )

    if not await auth_service.verify_otp(user, payload.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code. Codes expire after 15 minutes.",
        )

    await auth_service.clear_otp(user)
    # Use the email from the payload rather than trying to extract it from the user object
    # This avoids SQLAlchemy Column type issues
    return await auth_service.login_with_code(payload.email)

@recovery_router.post(
    "/reset-password", 
    status_code=status.HTTP_200_OK,
    response_model=PasswordResetResponse,
    summary="Reset password using a one-time code"
)
async def reset_password(payload: ResetPasswordSchema, db: AsyncSession = Depends(get_db)):
    """
    Resets a user's password using a one-time code sent to their email.
    
    This endpoint allows users to:
    - Set a new password after forgetting their current one
    - Complete the account recovery process
    - Secure their account with a new password
    
    The system will:
    1. Verify the user exists
    2. Validate the provided one-time code
    3. Update the user's password with the new one
    4. Clear the used one-time code
    
    Returns a success message upon password reset.
    
    Note: The new password must meet the system's password requirements:
    - At least 8 characters long
    - Contain a mix of uppercase, lowercase, numbers, and special characters
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address",
        )

    if not await auth_service.verify_otp(user, payload.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code. Codes expire after 15 minutes.",
        )

    # Password validation is handled in the update_password method
    
    # We need to get the user ID as an integer to avoid SQLAlchemy Column type issues
    try:
        user_id = int(str(user.id))
        
        # Use auth service to update password - this handles the ORM properly
        success = await auth_service.update_password(user_id, payload.new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update password. Please make sure it meets our security requirements."
            )
        
        await auth_service.clear_otp(user)
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )
    
    return {
        "message": "Password has been reset successfully. You can now log in with your new password.",
        "success": True
    }

@recovery_router.post(
    "/initiate-recovery",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Initiate account recovery process"
)
async def initiate_account_recovery(
    payload: AccountRecoveryRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    Unified endpoint that initiates the account recovery process.
    
    This is a more streamlined approach for mobile applications and SPAs that:
    1. Checks if the account exists
    2. Generates a one-time code
    3. Sends an email with the code and recovery instructions
    4. Optionally includes a custom recovery URL for frontend routing
    
    The email will contain:
    - A one-time code for authentication
    - Instructions for resetting the password
    - A link to the recovery page (if recovery_url is provided)
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(payload.email)
    
    # Always return the same message whether the email exists or not
    # This prevents user enumeration attacks
    response_message = {"message": "If your email is registered, recovery instructions will be sent."}
    
    if user:
        try:
            # Generate OTP code
            otp_code = await auth_service.create_otp(user)
            
            # Generate recovery link if URL is provided
            recovery_link = None
            if payload.recovery_url:
                recovery_link = f"{payload.recovery_url}?email={payload.email}&code={otp_code}"
            
            # Send the recovery email
            await email_service.send_account_recovery_email(
                to_email=payload.email,
                otp_code=otp_code,
                recovery_link=recovery_link
            )
            
            # For logging purposes only, don't change the user-facing message
            print(f"Recovery email sent to {payload.email}")
        except Exception as e:
            # Log the error but don't expose it to the client
            print(f"Error sending recovery email: {str(e)}")
            
    # Return the same generic message regardless of whether the email was sent
    # This is important for security to prevent user enumeration
    return response_message