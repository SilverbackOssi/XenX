from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from app.enterprises.models.enterprises import EnterpriseType

class EnterpriseBase(BaseModel):
    name: str
    email: str
    type: EnterpriseType
    tax_year: int
    description: Optional[str] = None
    country: str
    city: str
    address: Optional[str] = None
    website: Optional[str] = None
    
    # Branding fields
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    accent_color: Optional[str] = None
    footer_text: Optional[str] = None

class EnterpriseCreate(EnterpriseBase):
    pass

class EnterpriseUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    type: Optional[EnterpriseType] = None
    tax_year: Optional[int] = None
    description: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    
    # Branding fields
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    accent_color: Optional[str] = None
    footer_text: Optional[str] = None

class EnterpriseResponse(EnterpriseBase):
    id: int
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    staff_ids: List[int] = Field(default_factory=list)
    client_ids: List[int] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
