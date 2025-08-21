from pydantic import BaseModel, EmailStr
from app.auth.models.users import StaffRole

class StaffInvitation(BaseModel):
    email: EmailStr
    role: StaffRole
