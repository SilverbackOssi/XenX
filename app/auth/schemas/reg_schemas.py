from pydantic import BaseModel, EmailStr, constr, StringConstraints, Field
from typing import Optional, Annotated
# from app.auth.models.users import UserRole

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    password: str
    # role: UserRole = Field(UserRole.CPA, description="Role of the user (e.g., admin, cpa, client, staff)")
    last_name: Optional[str] = Field(None, description="Last name of the user")
    first_name: Optional[str] = Field(None, description="First name of the user")
    phone_number: Optional[str] = Field(None, description="Phone number of the user")



class UserResponse(BaseModel):
    """Schema for user creation response"""
    id: int
    email: str
    username: str
    # role: UserRole
    last_name: Optional[str]
    first_name: Optional[str]
    phone_number: Optional[str]
    is_active: bool
    email_verified: bool

    class Config:
        from_attributes = True
