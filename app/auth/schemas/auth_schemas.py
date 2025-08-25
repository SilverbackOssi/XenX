from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Union

class LoginRequest(BaseModel):
    """Schema for login request with either email or username"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str
    
    # Validate that either email or username is provided
    def model_post_init(self, __context):
        if not self.email and not self.username:
            raise ValueError("Either email or username must be provided")
            
class AccountRecoveryRequest(BaseModel):
    """Schema for initiating the account recovery process from a mobile app or SPA"""
    email: EmailStr = Field(..., description="Email address to recover")
    recovery_url: Optional[str] = Field(None, description="URL to include in email for frontend routing")

class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token payload"""
    sub: str  # user ID
    # role: str
    exp: Optional[int] = None

class RefreshRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str

class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class ForgotPasswordSchema(BaseModel):
    """Request schema for initiating password recovery process"""
    email: EmailStr = Field(..., description="Email address of the user requesting password recovery")

class LoginWithCodeSchema(BaseModel):
    """Request schema for logging in with a one-time code"""
    email: EmailStr = Field(..., description="Email address of the user")
    code: str = Field(..., min_length=6, max_length=6, description="Six-digit one-time password sent to user's email")

class ResetPasswordSchema(BaseModel):
    """Request schema for resetting password with a one-time code"""
    email: EmailStr = Field(..., description="Email address of the user")
    code: str = Field(..., min_length=6, max_length=6, description="Six-digit one-time password sent to user's email")
    new_password: str = Field(..., min_length=8, description="New password that meets security requirements")

class MessageResponse(BaseModel):
    """Standard success message response"""
    message: str = Field(..., description="Success message")

class LoginCodeResponse(BaseModel):
    """Response for login code request"""
    message: str = Field(..., description="Success message indicating code has been sent")

class PasswordResetResponse(BaseModel):
    """Response for password reset confirmation"""
    message: str = Field(..., description="Success message for password reset")
    success: bool = Field(..., description="Whether the operation was successful")
