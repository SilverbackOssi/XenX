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

class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token payload"""
    sub: str  # user ID
    role: str
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