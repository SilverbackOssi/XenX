from typing import Optional
from pydantic import BaseModel, Field

class BrandingUpdate(BaseModel):
    primary_color: Optional[str] = Field(None, description="Hex code for the primary brand color")
    accent_color: Optional[str] = Field(None, description="Hex code for the accent brand color")
    footer_text: Optional[str] = Field(None, description="Text to display in the footer of exported documents")
    logo_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "primary_color": "#00FF00",
                "accent_color": "#0000FF",
                "footer_text": "© 2025 Ziba LLC. All rights reserved."
            }
        }

class BrandingResponse(BaseModel):
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    accent_color: Optional[str] = None
    footer_text: Optional[str] = None

    class Config:
        from_attributes = True
