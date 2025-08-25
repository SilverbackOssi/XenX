from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.routes.routes import *
from app.auth.database import engine, Base

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
LOGOS_DIR = Path("uploads/logos")
LOGOS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="XenToba Gateway & User Management System", 
              version="0.1.0", 
              summary="XenToba GMS. Note: DB is not persistent at the moment.", 
              root_path="/api/v1")

# Include routers
app.include_router(auth_routes.auth_router)
app.include_router(password_reset_routes.recovery_router)
app.include_router(profile_routes.profile_router)
app.include_router(enterprise_routes.enterprise_router)
app.include_router(branding_routes.branding_router)
app.include_router(admin_routes.admin_router)

# sync tables
# Mount the uploads directory to make logos accessible
app.mount("/logos", StaticFiles(directory="uploads/logos"), name="logos")

@app.on_event("startup")
async def startup_event():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def index():
    return {"message": "Welcome to XenToba Gateway & User Management System",
            "next": "'#/docs' for documentation"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
