from pydantic import BaseModel, Field, EmailStr, StringConstraints
from typing import Optional, Annotated

class ChangePasswordRequest(BaseModel):
    """Schema for change password request"""
    old_password: str
    new_password: str = Field(..., min_length=8)
    
class UserUpdate(BaseModel):
    """Schema for user update"""
    email: Optional[EmailStr]
    username: Optional[Annotated[str, StringConstraints(min_length=3, max_length=50)]]
    last_name: Optional[str]
    first_name: Optional[str]
    phone_number: Optional[str]
