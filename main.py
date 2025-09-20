from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.gateway.routes.routes import *
from app.gateway.auth.database import engine, Base
from app.frontend import create_frontend_app
from app.gateway.auth.seeder import seed_database
from app.config import get_settings

import logging
settings = get_settings()
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads").mkdir(parents=True, exist_ok=True)
LOGOS_DIR = Path("uploads/logos").mkdir(parents=True, exist_ok=True)
TAX_RETURNS_DIR = Path("uploads/tax_returns").mkdir(parents=True, exist_ok=True)

# Main application
app = FastAPI(
    title="XenToba",
    description="Main application hosting the API and Frontend.",
    version="0.1.0"
)

# Create API app with versioned path
api_app = FastAPI(
    title="XenToba Gateway & User Management System",
    description="XenToba API",
    summary="XenToba GMS. Note: DB is not persistent at the moment.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to API app
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Gateway API routers
# Auth routes
api_app.include_router(google_oauth_router)
api_app.include_router(auth_routes.auth_router)
api_app.include_router(recovery.recovery_router)
api_app.include_router(profile_routes.profile_router)

# Enterprise/Organization routes
api_app.include_router(enterprise_routes.enterprise_router)
api_app.include_router(branding_routes.branding_router)
api_app.include_router(staff_routes.staff_router)
api_app.include_router(staff_routes.client_router)
api_app.include_router(project_router)
api_app.include_router(strategy_router)
api_app.include_router(client_goal_router)
api_app.include_router(tax_plan_router)

# Admin/Demo routes
api_app.include_router(admin_router)

@api_app.get("/")
def api_index():
    return {"message": "Welcome to XenToba API",
            "docs": "/docs for API documentation"}

@api_app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Create Frontend app
frontend_app = create_frontend_app()

# Mount the uploads directories to make files accessible
app.mount("/logos", StaticFiles(directory="uploads/logos"), name="logos")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Mount API and Frontend apps
app.mount("/api/v1", api_app)
app.mount("/", frontend_app)

@app.get("/api/v1/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return api_app.openapi()

# @app.on_event("startup")
# async def startup_event():
#     # Create database tables for main app
#     async with engine.begin() as conn:
#         # Run database seeder to populate with test data
#         if settings.RUN_SEEDER_ON_STARTUP:
#             try:
#                 await conn.run_sync(Base.metadata.drop_all)
#             except Exception as e:
#                 # Ignore errors when dropping tables that don't exist
#                 logger.warning(f"Warning dropping tables (this is normal on first run): {e}")
            
#             await conn.run_sync(Base.metadata.create_all)
#             try:
#                 logger.info("🌱 Running database seeder...")
#                 await seed_database()
#                 logger.info("✅ Database seeded successfully!")
#             except Exception as e:
#                 logger.error(f"❌ Error seeding database: {e}")
#                 # Don't fail startup if seeding fails
#         else:
#             # Just create tables without seeding
#             await conn.run_sync(Base.metadata.create_all)
#             logger.info("✅ Database tables created!")
    
#     # Initialize Tax Planner microservice database
#     from app.microservices.tax_planner.tp_database import init_tp_db
#     try:
#         logger.info("🔄 Initializing Tax Planner database...")
#         await init_tp_db()
#         logger.info("✅ Tax Planner database initialized successfully!")
#     except Exception as e:
#         logger.error(f"❌ Error initializing Tax Planner database: {e}")




