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

class SimpleEnterpriseResponse(BaseModel):
    """Simplified schema for enterprise info in profile (id, name, type only)"""
    id: int
    name: str
    type: EnterpriseType
    
    class Config:
        from_attributes = True

class SimpleStaffEnterpriseResponse(BaseModel):
    """Simplified schema for staff enterprises in profile (id, name, type, role only)"""
    id: int
    name: str
    type: EnterpriseType
    role: StaffRole
    
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
    owned_enterprises: List[SimpleEnterpriseResponse] = Field(default_factory=list)
    staff_enterprises: List[SimpleStaffEnterpriseResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
