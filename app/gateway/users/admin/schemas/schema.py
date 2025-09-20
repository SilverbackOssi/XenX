from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.gateway.auth.schemas.user_schemas import UserCreate
from app.gateway.users.user.models.users import SubscriptionPlans


# Define admin-specific schemas
class UserCreateAdmin(UserCreate):
    """Schema for admin to create users with additional fields"""
    is_active: bool = True
    is_superuser: bool = False
    email_verified: bool = False

class UserUpdateAdmin(BaseModel):
    """Schema for admin to update users"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    email_verified: Optional[bool] = None
    subscription_plan: Optional[SubscriptionPlans] = None

class UserSubscriptionUpdate(BaseModel):
    """Schema for updating user subscription"""
    subscription_plan: SubscriptionPlans

class UsersCreateBatch(BaseModel):
    """Schema for batch user creation"""
    users: List[UserCreateAdmin]
