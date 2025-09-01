from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.routes.routes import *
from app.auth.database import engine, Base
from app.frontend import init_frontend
from app.auth.seeder import seed_database
from app.config import get_settings

import logging
settings = get_settings()
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads").mkdir(parents=True, exist_ok=True)
LOGOS_DIR = Path("uploads/logos").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="XenToba API Demo Frontend", 
              version="0.1.0", 
              description="Frontend routes for the XenToba API")

# Create API app with versioned path
api_app = FastAPI(
    title="XenToba Gateway & User Management System",
    description="XenToba API",
    summary="XenToba GMS. Note: DB is not persistent at the moment.",
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
api_app.include_router(staff_routes.staff_router)
api_app.include_router(staff_routes.client_router)
api_app.include_router(admin_routes.admin_router)
api_app.include_router(google_oauth_router)




# Initialize frontend
init_frontend(app)

# sync tables
# Mount the uploads directory to make logos accessible
app.mount("/logos", StaticFiles(directory="uploads/logos"), name="logos")

@app.on_event("startup")
async def startup_event():
    # Create database tables
    async with engine.begin() as conn:
        # Run database seeder to populate with test data
        if settings.RUN_SEEDER_ON_STARTUP:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            try:
                logger.info("🌱 Running database seeder...")
                await seed_database()
                logger.info("✅ Database seeded successfully!")
            except Exception as e:
                logger.error(f"❌ Error seeding database: {e}")
            # Don't fail startup if seeding fails
    
        

@api_app.get("/")
def api_index():
    return {"message": "Welcome to XenToba API",
            "docs": "/docs for API documentation"}

@api_app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Mount API app under /api/v1
app.mount("/api/v1", api_app)
