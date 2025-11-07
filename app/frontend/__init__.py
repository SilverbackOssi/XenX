from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

def create_frontend_app():
    """Create and configure the frontend FastAPI app"""
    frontend_app = FastAPI(
        title="XenToba Frontend",
        description="Frontend interface for XenToba",
        version="0.1.0",
        docs_url=None,
        redoc_url=None
    )
    
    # Mount static files
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        frontend_app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    # Serve the main HTML file
    @frontend_app.get("/{path:path}")
    async def serve_frontend(path: str = ""):
        """Serve the frontend HTML file for all routes (SPA)"""
        template_path = Path(__file__).parent / "templates" / "index.html"
        if template_path.exists():
            return FileResponse(str(template_path))
        else:
            return {"error": "Frontend not found", "path": str(template_path)}
    
    return frontend_app
