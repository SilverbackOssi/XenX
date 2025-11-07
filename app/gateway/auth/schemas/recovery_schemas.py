from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any

class RequestOTPSchema(BaseModel):
    """Schema for requesting a one-time password via email"""
    email: EmailStr = Field(..., description="User's email address")

class OTPRequestResponse(BaseModel):
    """Response for OTP request"""
    message: str
    email_sent: bool
    expires_in_minutes: int = 10

class VerifyOTPSchema(BaseModel):
    """Schema for verifying a one-time password"""
    email: EmailStr = Field(..., description="User's email address")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")

class ResetPasswordSchema(BaseModel):
    """Schema for resetting password with OTP"""
    email: EmailStr = Field(..., description="User's email address")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    new_password: str = Field(
        ..., 
        min_length=8, 
        description="New password (minimum 8 characters)"
    )
    confirm_password: str = Field(
        ..., 
        min_length=8, 
        description="Confirm new password"
    )
    
    # Validate that passwords match
    def model_post_init(self, __context):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")

class PasswordResetResponse(BaseModel):
    """Response for password reset"""
    message: str
    success: bool

class LoginWithOTPSchema(BaseModel):
    """Schema for login with OTP"""
    email: EmailStr = Field(..., description="User's email address")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")

class LoginResponse(BaseModel):
    """Response for successful login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]
