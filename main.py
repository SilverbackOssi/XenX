from fastapi import FastAPI
from app.routes import auth
from app.auth.database import engine, Base

app = FastAPI(title="XenToba Gateway & User Management System")

# Include routers
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
