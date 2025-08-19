from fastapi import FastAPI
from app.routes.routes import auth_router
from app.auth.database import engine, Base

app = FastAPI(title="XenToba Gateway & User Management System")

# Include routers
app.include_router(auth_router)

# sync tables
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
