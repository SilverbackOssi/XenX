from pydantic import BaseModel, EmailStr, Field
from typing import List
from app.auth.models.users import StaffRole

class StaffInvitationItem(BaseModel):
    email: EmailStr
    role: StaffRole

class StaffInvitation(BaseModel):
    email: EmailStr
    role: StaffRole

class MultipleStaffInvitations(BaseModel):
    invitations: List[StaffInvitationItem]
