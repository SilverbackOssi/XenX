from fastapi import FastAPI
from app.routes.routes import *
# from app.auth.password_reset_routes import router as password_reset_router
from app.auth.database import engine, Base

app = FastAPI(title="XenToba Gateway & User Management System")

# Include routers
app.include_router(auth_routes.auth_router)
app.include_router(profile_routes.profile_router)
app.include_router(enterprise_routes.enterprise_router)
app.include_router(dev_routes.dev_router)
# app.include_router(password_reset_router, prefix="/auth", tags=["auth"])

# sync tables
@app.on_event("startup")
async def startup_event():
    # Create database tables
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def index():
    return {"message": "Welcome to XenToba Gateway & User Management System",
            "next": "'#/docs' for documentation"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
