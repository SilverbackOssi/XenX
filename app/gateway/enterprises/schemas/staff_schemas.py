from pydantic import BaseModel, EmailStr, Field
from typing import List
from ..models.enterprises import StaffRole, StaffPermission

# class StaffInvitationItem(BaseModel):
#     email: EmailStr
#     role: StaffRole
#     permission: StaffPermission

class StaffInvitation(BaseModel):
    email: EmailStr
    role: StaffRole
    permission: StaffPermission

class MultipleStaffInvitations(BaseModel):
    invitations: List[StaffInvitation]

class StaffPermissionUpdate(BaseModel):
    email: EmailStr
    role: StaffRole
    permission: StaffPermission

class StaffResponse(BaseModel):
    email: EmailStr
    role: StaffRole
    permission: StaffPermission
    enterprise_id: int
    invited_by: int
    invited_staff_ids: List[int]
    invited_client_ids: List[int]
    is_active: bool