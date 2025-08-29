
from fastapi import APIRouter, UploadFile, File, Depends
from typing import List, Optional

router = APIRouter()

# --- Project Endpoints ---
@router.post("/enterprises/{enterprise_id}/projects", summary="Create a new project")
async def create_project(enterprise_id: int):
    pass

@router.get("/enterprises/{enterprise_id}/projects", summary="List all projects for an enterprise")
async def list_projects(enterprise_id: int):
    pass

@router.get("/projects/{project_id}", summary="Get project details")
async def get_project(project_id: int):
    pass

@router.put("/projects/{project_id}", summary="Update a project")
async def update_project(project_id: int):
    pass

@router.delete("/projects/{project_id}", summary="Delete a project")
async def delete_project(project_id: int):
    pass

# --- File Upload Endpoint (for verification doc, via project) ---
@router.post("/projects/{project_id}/upload_verification_doc", summary="Upload verification document for a project's tax entity")
async def upload_verification_doc(project_id: int, file: UploadFile = File(...)):
    pass

