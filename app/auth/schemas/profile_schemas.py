from pydantic import BaseModel, Field, EmailStr, StringConstraints
from typing import Optional, Annotated, List
from datetime import datetime
from app.enterprises.models.enterprises import EnterpriseType
from app.enterprises.models.permissions import StaffRole, StaffPermission

class ChangePasswordRequest(BaseModel):
    """Schema for change password request"""
    old_password: str
    new_password: str = Field(..., min_length=8)
    
class UserUpdate(BaseModel):
    """Schema for user update"""
    email: Optional[EmailStr] = None
    username: Optional[Annotated[str, StringConstraints(min_length=3, max_length=50)]] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    phone_number: Optional[str] = None

class OwnedEnterpriseResponse(BaseModel):
    """Schema for enterprises owned by the user"""
    id: int
    name: str
    email: str
    type: EnterpriseType
    tax_year: int
    description: Optional[str] = None
    country: str
    city: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    staff_count: int = 0
    client_count: int = 0
    
    class Config:
        from_attributes = True

class StaffEnterpriseResponse(BaseModel):
    """Schema for enterprises where user is a staff member"""
    id: int
    name: str
    email: str
    type: EnterpriseType
    country: str
    city: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    role: StaffRole
    permission: StaffPermission
    is_active: bool
    joined_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    """Enhanced schema for complete user profile including enterprises"""
    id: int
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    subscription_plan: str
    is_active: bool
    email_verified: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    # Enterprise relationships
    owned_enterprises: List[OwnedEnterpriseResponse] = Field(default_factory=list)
    staff_enterprises: List[StaffEnterpriseResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
