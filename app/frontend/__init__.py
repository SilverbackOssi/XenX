"""
Frontend serving module for the XenToba application.
This module allows serving the frontend static files and templates.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Set up templates directory
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Create frontend router
frontend_router = APIRouter(tags=["Frontend"])

@frontend_router.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    """Serve the main frontend application"""
    return templates.TemplateResponse("index.html", {"request": request})

@frontend_router.get("/admin", response_class=HTMLResponse)
async def serve_admin(request: Request):
    """Serve the admin page"""
    return templates.TemplateResponse("index.html", {"request": request})

@frontend_router.get("/auth", response_class=HTMLResponse)
async def serve_auth(request: Request):
    """Serve the auth page"""
    return templates.TemplateResponse("index.html", {"request": request})

@frontend_router.get("/tentants", response_class=HTMLResponse)
async def serve_tentants(request: Request):
    """Serve the tentants page"""
    return templates.TemplateResponse("index.html", {"request": request})

@frontend_router.get("/api-explorer", response_class=HTMLResponse)
async def serve_api_explorer(request: Request):
    """Serve the API explorer page"""
    return templates.TemplateResponse("index.html", {"request": request})

@frontend_router.get("/google-callback", response_class=HTMLResponse)
async def google_callback(request: Request, access_token: str = "", refresh_token: str = ""):
    """Handle Google OAuth callback and pass tokens to the frontend"""
    # Pass tokens as template variables so JavaScript can access them
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    )

# Function to initialize and mount static files
def init_frontend(app):
    """
    Initialize the frontend by mounting static files and including the router
    
    Args:
        app: FastAPI application instance
    """
    # Mount static files
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Include the frontend router
    app.include_router(frontend_router)
