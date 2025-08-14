from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)

class UserCreate(UserBase):
    password: constr(min_length=8)
    organization_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    created_at: datetime
    roles: List[str]
    organizations: List[str]

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshToken(BaseModel):
    refresh_token: str

class MFAEnrollResponse(BaseModel):
    secret_key: str
    qr_code: str
    backup_codes: List[str]

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: constr(min_length=8)

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str]

class PermissionCreate(BaseModel):
    resource: str
    action: str

class OrganizationCreate(BaseModel):
    name: str
    subscription_tier: Optional[str] = "basic"
