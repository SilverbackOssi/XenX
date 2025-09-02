from typing import Tuple, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload
from fastapi import UploadFile, HTTPException, status
import os
import shutil
import uuid
from datetime import datetime

from app.microservices.tax_planner.models.projects import Project, TaxEntity
from app.microservices.tax_planner.schemas.project_schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.config import get_settings

settings = get_settings()

class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_project(self, enterprise_id: int, project_data: ProjectCreate, tax_return: UploadFile) -> Tuple[Optional[ProjectResponse], Optional[str]]:
        """Create a new project with a tax entity and upload tax return document"""
        try:
            # First, save the tax return document
            file_url = await self._save_tax_return(enterprise_id, tax_return)
            
            # Create tax entity
            tax_entity = TaxEntity(
                industry=project_data.tax_entity.industry,
                jurisdiction=project_data.tax_entity.jurisdiction,
                filing_status=project_data.tax_entity.filing_status,
                currency=project_data.tax_entity.currency,
                entity_type=project_data.tax_entity.entity_type,
                tax_year=project_data.tax_entity.tax_year,
                additional_notes=project_data.tax_entity.additional_notes,
                tax_return_doc_url=file_url
            )
            
            self.db.add(tax_entity)
            await self.db.flush()  # Get the tax_entity.id
            
            # Create project
            project = Project(
                enterprise_id=enterprise_id,
                tax_entity_id=tax_entity.id,
                project_name=project_data.project_name,
                project_type=project_data.project_type,
                client_name=project_data.client_name,
                client_phone_number=project_data.client_phone_number,
                client_email=project_data.client_email
            )
            
            self.db.add(project)
            await self.db.commit()
            await self.db.refresh(project)
            await self.db.refresh(tax_entity)
            
            # Construct response
            response = self._project_to_response(project, tax_entity)
            
            return response, None
        except Exception as e:
            await self.db.rollback()
            return None, str(e)
    
    async def get_projects(self, enterprise_id: int) -> Tuple[Optional[List[ProjectResponse]], Optional[str]]:
        """Get all projects for an enterprise"""
        try:
            # Query projects with their associated tax entities
            query = select(Project).filter(Project.enterprise_id == enterprise_id)
            result = await self.db.execute(query)
            projects = result.scalars().all()
            
            if not projects:
                return [], None
            
            # Load tax entities for each project
            project_responses = []
            for project in projects:
                tax_entity = await self.db.get(TaxEntity, project.tax_entity_id)
                if tax_entity:
                    project_responses.append(self._project_to_response(project, tax_entity))
            
            return project_responses, None
        except Exception as e:
            return None, str(e)
    
    async def get_project(self, enterprise_id: int, project_id: int) -> Tuple[Optional[ProjectResponse], Optional[str]]:
        """Get a specific project by ID"""
        try:
            # Get project and verify it belongs to the enterprise
            project = await self.db.get(Project, project_id)
            
            if not project:
                return None, "Project not found"
                
            # Use int() to convert SQLAlchemy Column to Python int for comparison
            if int(project.enterprise_id) != enterprise_id:  # type: ignore
                return None, "Project doesn't belong to this enterprise"
            
            # Get the associated tax entity
            tax_entity = await self.db.get(TaxEntity, project.tax_entity_id)
            if not tax_entity:
                return None, "Tax entity not found for this project"
            
            # Construct response
            response = self._project_to_response(project, tax_entity)
            
            return response, None
        except Exception as e:
            return None, str(e)
    
    async def update_project(self, enterprise_id: int, project_id: int, project_data: ProjectUpdate) -> Tuple[Optional[ProjectResponse], Optional[str]]:
        """Update a project and its tax entity"""
        try:
            # Get project and verify it belongs to the enterprise
            project = await self.db.get(Project, project_id)
            
            if not project:
                return None, "Project not found"
                
            # Use int() to convert SQLAlchemy Column to Python int for comparison
            if int(project.enterprise_id) != enterprise_id:  # type: ignore
                return None, "Project doesn't belong to this enterprise"
            
            # Update project fields
            for key, value in project_data.dict(exclude_unset=True, exclude={"tax_entity"}).items():
                if value is not None:
                    setattr(project, key, value)
            
            # Update tax entity if provided
            if project_data.tax_entity:
                tax_entity = await self.db.get(TaxEntity, project.tax_entity_id)
                if not tax_entity:
                    return None, "Tax entity not found for this project"
                
                for key, value in project_data.tax_entity.items():
                    if value is not None:
                        setattr(tax_entity, key, value)
            
            await self.db.commit()
            await self.db.refresh(project)
            
            # Get the updated tax entity
            tax_entity = await self.db.get(TaxEntity, project.tax_entity_id)
            
            # Construct response
            response = self._project_to_response(project, tax_entity)
            
            return response, None
        except Exception as e:
            await self.db.rollback()
            return None, str(e)
    
    async def delete_project(self, enterprise_id: int, project_id: int) -> Tuple[bool, Optional[str]]:
        """Delete a project and its tax entity"""
        try:
            # Get project and verify it belongs to the enterprise
            project = await self.db.get(Project, project_id)
            
            if not project:
                return False, "Project not found"
                
            # Use int() to convert SQLAlchemy Column to Python int for comparison
            if int(project.enterprise_id) != enterprise_id:  # type: ignore
                return False, "Project doesn't belong to this enterprise"
            
            # Get tax entity to delete it first (due to foreign key constraint)
            tax_entity_id = project.tax_entity_id
            
            # Delete project
            await self.db.delete(project)
            
            # Delete tax entity
            tax_entity = await self.db.get(TaxEntity, tax_entity_id)
            if tax_entity:
                await self.db.delete(tax_entity)
            
            await self.db.commit()
            
            return True, None
        except Exception as e:
            await self.db.rollback()
            return False, str(e)
    
    async def upload_tax_return(self, enterprise_id: int, project_id: int, file: UploadFile) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
        """Upload or replace a tax return document for a project"""
        try:
            # Get project and verify it belongs to the enterprise
            project = await self.db.get(Project, project_id)
            
            if not project:
                return None, "Project not found"
                
            # Use int() to convert SQLAlchemy Column to Python int for comparison
            if int(project.enterprise_id) != enterprise_id:  # type: ignore
                return None, "Project doesn't belong to this enterprise"
            
            # Get tax entity to update its document URL
            tax_entity = await self.db.get(TaxEntity, project.tax_entity_id)
            if not tax_entity:
                return None, "Tax entity not found for this project"
            
            # Save the new tax return document
            file_url = await self._save_tax_return(enterprise_id, file)
            
            # Update tax entity with new document URL using setattr
            setattr(tax_entity, "tax_return_doc_url", file_url)
            await self.db.commit()
            
            # Ensure file.filename is not None
            filename = file.filename or "unknown_file"
            
            # Create response dict with all string values
            response = {
                "filename": filename,
                "file_url": file_url,
                "message": "Tax return document uploaded successfully"
            }
            
            return response, None
        except Exception as e:
            await self.db.rollback()
            return None, str(e)
    
    async def _save_tax_return(self, enterprise_id: int, file: UploadFile) -> str:
        """Save a tax return document and return its URL"""
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(settings.UPLOAD_DIR, "tax_returns", str(enterprise_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return the relative URL
        return f"/uploads/tax_returns/{enterprise_id}/{unique_filename}"
    
    def _project_to_response(self, project: Project, tax_entity: TaxEntity) -> ProjectResponse:
        """
        Convert SQLAlchemy models to Pydantic response objects
        Using dictionary conversion and from_orm to handle SQLAlchemy column types
        """
        from app.microservices.tax_planner.schemas.project_schemas import ProjectResponse, TaxEntityResponse
        
        # First create dicts from the model objects
        tax_entity_dict = {}
        for column in tax_entity.__table__.columns:
            tax_entity_dict[column.name] = getattr(tax_entity, column.name)
        
        project_dict = {}
        for column in project.__table__.columns:
            if column.name != 'tax_entity_id':  # Skip this as we'll include the full tax_entity
                project_dict[column.name] = getattr(project, column.name)
        
        # Create the tax entity response first
        tax_entity_response = TaxEntityResponse.model_validate(tax_entity_dict)
        
        # Add it to the project dict
        project_dict['tax_entity'] = tax_entity_response
        
        # Create the final response
        return ProjectResponse.model_validate(project_dict)
