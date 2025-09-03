
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.microservices.tax_planner.tp_database import get_db
from app.microservices.tax_planner.schemas.project_schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, FileUploadResponse
)
from app.microservices.tax_planner.services.project_service import ProjectService
from app.auth.services.token_service import TokenService
from app.auth.models.users import User

project_router = APIRouter(prefix="/enterprises", tags=["Enterprise Projects"])

# --- Project Endpoints ---
@project_router.post(
    "/{enterprise_id}/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED,
    summary="Create a new project"
)
async def create_project(
    enterprise_id: int, project_data: ProjectCreate, tax_return: UploadFile = File(...), db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    Create a new tax planning project with associated tax entity.
    Requires:
    - Project data (name, type, client details)
    - Tax entity data (entity type, industry, jurisdiction, etc.)
    - Tax return document file
    """
    project_service = ProjectService(db)
    result, error = await project_service.create_project(enterprise_id, project_data, tax_return)
    
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
        
    return result

@project_router.get(
    "/{enterprise_id}/projects", response_model=List[ProjectResponse], status_code=status.HTTP_200_OK,
    summary="List all projects for an enterprise"
)
async def list_projects(
    enterprise_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    List all tax planning projects for an enterprise.
    Returns a list of projects with their associated tax entities.
    """
    project_service = ProjectService(db)
    projects, error = await project_service.get_projects(enterprise_id)
    
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
        
    return projects

@project_router.get(
    "/{enterprise_id}/projects/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK,
    summary="Get project details"
)
async def get_project(
    enterprise_id: int, project_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    Get detailed information about a specific tax planning project.
    Returns project data with its associated tax entity.
    """
    project_service = ProjectService(db)
    project, error = await project_service.get_project(enterprise_id, project_id)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if error == "Project not found" else status.HTTP_400_BAD_REQUEST,
            detail=error
        )
        
    return project

@project_router.put(
    "/{enterprise_id}/projects/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK,
    summary="Update a project"
)
async def update_project(
    enterprise_id: int, project_id: int, project_data: ProjectUpdate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    Update an existing tax planning project.
    Can update project details and/or tax entity details.
    """
    project_service = ProjectService(db)
    updated_project, error = await project_service.update_project(enterprise_id, project_id, project_data)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if error == "Project not found" else status.HTTP_400_BAD_REQUEST,
            detail=error
        )
        
    return updated_project

@project_router.delete("/{enterprise_id}/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT, 
                       summary="Delete a project")
async def delete_project(
    enterprise_id: int, project_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    Delete a tax planning project and its associated tax entity.
    """
    project_service = ProjectService(db)
    success, error = await project_service.delete_project(enterprise_id, project_id)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if error == "Project not found" else status.HTTP_400_BAD_REQUEST,
            detail=error
        )
        
    return None  # 204 No Content

# --- File Upload Endpoint (for tax return doc, via project) ---
@project_router.post(
    "/{enterprise_id}/projects/{project_id}/upload-tax-return", 
    response_model=FileUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload tax return document for a project's tax entity"
)
async def upload_tax_return_doc(
    enterprise_id: int, project_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    Upload or replace the tax return document for a project's tax entity.
    """
    project_service = ProjectService(db)
    result, error = await project_service.upload_tax_return(enterprise_id, project_id, file)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if error == "Project not found" else status.HTTP_400_BAD_REQUEST,
            detail=error
        )
        
    return result

