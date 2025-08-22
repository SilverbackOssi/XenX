import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database import get_db
from app.auth.models.users import User
from app.auth.services.token_service import TokenService
from app.enterprises.models.enterprises import Enterprise
from app.enterprises.services.enterprise_service import EnterpriseService
from app.enterprises.schemas.branding_schemas import BrandingUpdate, BrandingResponse

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads/logos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

branding_router = APIRouter(prefix="/enterprises", tags=["Enterprise Branding"])

@branding_router.post("/{enterprise_id}/branding/logo", status_code=status.HTTP_200_OK)
async def upload_logo(
    enterprise_id: int,
    logo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Upload a logo for the enterprise.
    Requires permission
    """
    enterprise_service = EnterpriseService(db)
    
    # Get enterprise by ID
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    # Verify user has permission to update this enterprise
    if not await enterprise_service.has_permission(enterprise, current_user.id): # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this enterprise"
        )
    
    # Check file type (allow common image formats)
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".svg"}
    filename = logo.filename or "" # Potential bug
    file_ext = os.path.splitext(filename)[1].lower() # refactor for better processing
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create a unique filename
    filename = f"enterprise_{enterprise_id}{file_ext}"
    file_path: Path = UPLOAD_DIR / filename
    
    # Save the file
    try:
        # Delete existing logo if it exists
        if enterprise is not None and getattr(enterprise, "logo_url", None) is not None:
            old_file_path = Path(enterprise.logo_url.replace("/logos/", "uploads/logos/"))
            if old_file_path.exists():
                os.remove(old_file_path)
        
        # Save the new logo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)
        
        # Update the database with the logo URL
        logo_url = f"/logos/{filename}"
        enterprise, error = await enterprise_service.update_enterprise_branding(
            enterprise_id=enterprise_id, 
            branding_data={"logo_url": logo_url}
        )
        
        if error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
            
        return {"message": "Logo uploaded successfully", "logo_url": logo_url}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@branding_router.delete("/{enterprise_id}/branding/logo", status_code=status.HTTP_200_OK)
async def delete_logo(
    enterprise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Delete the enterprise logo.
    Requires permission
    """
    enterprise_service = EnterpriseService(db)

    # Get enterprise by ID
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    # Verify user has permission to update this enterprise
    if not await enterprise_service.has_permission(enterprise, current_user.id): # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this enterprise"
        )
    
    # Check if a logo exists
    if enterprise is None or getattr(enterprise, "logo_url", None) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No logo found for this enterprise"
        )
    
    # Delete the logo file
    try:
        file_path = Path(enterprise.logo_url.replace("/logos/", "uploads/logos/"))
        if file_path.exists():
            os.remove(file_path)
        
        # Update the database to remove the logo URL
        enterprise, error = await enterprise_service.update_enterprise_branding(
            enterprise_id=enterprise_id, 
            branding_data={"logo_url": None}
        )
        
        if error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
            
        return {"message": "Logo deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@branding_router.post("/{enterprise_id}/branding", status_code=status.HTTP_200_OK)
async def add_branding(
    enterprise_id: int,
    branding_data: BrandingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Set branding information for the enterprise.
    Requires permission
    """
    enterprise_service = EnterpriseService(db)

    # Get enterprise by ID
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    # Verify user has permission to update this enterprise
    if not await enterprise_service.has_permission(enterprise, current_user.id): # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this enterprise"
        )
    
    # Update the branding
    enterprise, error = await enterprise_service.update_enterprise_branding(
        enterprise_id=enterprise_id,
        branding_data=branding_data.model_dump(exclude_unset=True)
    )
    
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
        
    return {"message": "Branding updated successfully", "branding": enterprise}

@branding_router.patch("/{enterprise_id}/branding", status_code=status.HTTP_200_OK)
async def update_branding(
    enterprise_id: int,
    branding_data: BrandingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Update branding information for the enterprise.
    Requires permission
    """
    enterprise_service = EnterpriseService(db)
    
    # Get enterprise by ID
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    # Verify user has permission to update this enterprise
    if not await enterprise_service.has_permission(enterprise, current_user.id): # pyright: ignore[reportArgumentType]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this enterprise"
        )
    
    # Update the branding
    enterprise, error = await enterprise_service.update_enterprise_branding(
        enterprise_id=enterprise_id,
        branding_data=branding_data.model_dump(exclude_unset=True)
    )
    
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
        
    return {"message": "Branding updated successfully", "branding": enterprise}

@branding_router.get("/{enterprise_id}/branding", status_code=status.HTTP_200_OK, response_model=BrandingResponse)
async def get_branding(
    enterprise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user),
):
    """
    Get branding information for the enterprise.
    Requires permission
    """
    enterprise_service = EnterpriseService(db)
    
    # Get enterprise by ID
    enterprise, error = await enterprise_service.get_enterprise_by_id(enterprise_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    # Verify user has permission to view this enterprise
    if not await enterprise_service.has_permission(enterprise, current_user.id): # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this enterprise"
        )
    
    # Return the branding information
    return BrandingResponse(
        logo_url=enterprise.logo_url,
        primary_color=enterprise.primary_color,
        accent_color=enterprise.accent_color,
        footer_text=enterprise.footer_text
    )
