
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.microservices.tax_planner.models.projects import ProjectType, EntityType, FilingStatus

class TaxEntityBase(BaseModel):
    """Base schema for tax entity data"""
    entity_type: EntityType
    industry: str
    jurisdiction: str
    filing_status: FilingStatus
    currency: str = "USD"
    tax_year: str

class TaxEntityCreate(TaxEntityBase):
    """Schema for creating a tax entity"""
    additional_notes: Optional[str] = None

class TaxEntityResponse(TaxEntityBase):
    """Schema for tax entity response data"""
    id: int
    additional_notes: Optional[str] = None
    tax_return_doc_url: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    """Base schema for project data"""
    enterprise_id: int
    project_name: str
    project_type: ProjectType = ProjectType.TAX_PLANNING
    client_name: Optional[str] = None
    client_phone_number: Optional[str] = None
    client_email: Optional[str] = None

class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    tax_entity: TaxEntityCreate

class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    project_name: Optional[str] = None
    project_type: Optional[ProjectType] = None
    client_name: Optional[str] = None
    client_phone_number: Optional[str] = None
    client_email: Optional[str] = None
    
    tax_entity: Optional[dict] = None

class ProjectResponse(ProjectBase):
    """Schema for project response data"""
    id: int
    tax_entity: TaxEntityResponse
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    filename: str
    file_url: str
    message: str