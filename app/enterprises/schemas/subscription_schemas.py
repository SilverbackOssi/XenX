from pydantic import BaseModel
from typing import Optional
from datetime import datetime
# from app.auth.models.subscriptions import PlanType

class PlanBase(BaseModel):
    name: str
    price: float
    currency: str = "USD"
    features: Optional[str] = None
    user_limit: Optional[int] = None
    storage_limit_gb: Optional[int] = None
    is_active: bool = True

class PlanCreate(PlanBase):
    pass

class PlanResponse(PlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
