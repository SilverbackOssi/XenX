from pydantic import BaseModel, Field

class ChangePasswordRequest(BaseModel):
    """Schema for change password request"""
    old_password: str
    new_password: str = Field(..., min_length=8)
    