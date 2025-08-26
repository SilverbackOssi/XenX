from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.routes.routes import *
from app.auth.database import engine, Base
from app.frontend import init_frontend

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
LOGOS_DIR = Path("uploads/logos")
LOGOS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="XenToba Gateway & User Management System", 
              version="0.1.0", 
              summary="XenToba GMS. Note: DB is not persistent at the moment.")

# Create API app with versioned path
api_app = FastAPI(
    title="XenToba API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API routers
api_app.include_router(auth_routes.auth_router)
api_app.include_router(password_reset_routes.recovery_router)
api_app.include_router(profile_routes.profile_router)
api_app.include_router(enterprise_routes.enterprise_router)
api_app.include_router(branding_routes.branding_router)
api_app.include_router(admin_routes.admin_router)
api_app.include_router(google_oauth_router)

# Mount API app under /api/v1
app.mount("/api/v1", api_app)

# Initialize frontend
init_frontend(app)

# sync tables
# Mount the uploads directory to make logos accessible
app.mount("/logos", StaticFiles(directory="uploads/logos"), name="logos")

@api_app.on_event("startup")
async def startup_event():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@api_app.get("/")
def api_index():
    return {"message": "Welcome to XenToba API",
            "docs": "/docs for API documentation"}

@api_app.get("/health")
async def health_check():
    return {"status": "healthy"}
