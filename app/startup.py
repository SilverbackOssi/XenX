import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.auth.seeder import seed_database
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events.
    This will run the database seeder on startup if in development mode.
    """
    # Startup
    logger.info("🚀 Application startup")
    
    if settings.ENVIRONMENT == "development" and settings.DEBUG:
        try:
            logger.info("🌱 Running database seeder in development mode...")
            await seed_database()
        except Exception as e:
            logger.error(f"❌ Failed to seed database: {e}")
            # Don't fail the startup, just log the error
    
    yield
    
    # Shutdown
    logger.info("🛑 Application shutdown")
