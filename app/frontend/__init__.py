"""
Frontend serving module for the XenToba application.
This module allows serving the frontend static files and templates.
"""

from fastapi import APIRouter, Request, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

def create_frontend_app():
    """
    Create and configure the frontend FastAPI application.
    """
    frontend_app = FastAPI(
        title="XenToba Frontend",
        description="Serves the frontend for XenToba application.",
        version="0.1.0"
    )

    # Set up templates directory
    templates_dir = Path(__file__).parent / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))

    # Mount static files
    static_dir = Path(__file__).parent / "static"
    frontend_app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

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

    @frontend_router.get("/enterprises", response_class=HTMLResponse)
    async def serve_enterprises(request: Request):
        """Serve the enterprises page"""
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

    # Include the frontend router
    frontend_app.include_router(frontend_router)
    
    return frontend_app
