from pydantic import BaseModel
from typing import Optional
from datetime import datetime
# from app.enterprises.models.enterprises 
from app.enterprises.models.enterprises import EnterpriseType

class EnterpriseBase(BaseModel):
    name: str
    email: str
    type: EnterpriseType
    default_tax_year: int
    country: str
    city: str
    website: Optional[str] = None
    description: Optional[str] = None

class EnterpriseCreate(EnterpriseBase):
    pass

class EnterpriseResponse(EnterpriseBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
