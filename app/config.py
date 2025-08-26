import os
import logging
from typing import Dict, Any, Optional, Union, List
from functools import lru_cache
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("app.config")


class Settings(BaseSettings):
    """
    Central configuration settings for the XenX application.
    All environment variables should be defined here.
    """
    # Application Settings
    APP_NAME: str = "XenX"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # API URLs
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://xenx.onrender.com")
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://xentoba.pxxl.pro")
    FRONTEND_LOGIN_URL: str = os.getenv("FRONTEND_LOGIN_URL", "https://xentoba.pxxl.pro/login")
    FRONTEND_REGISTER_URL: str = os.getenv("FRONTEND_REGISTER_URL", "https://xentoba.pxxl.pro/register")
    
    # Database Settings
    USERS_DATABASE_URL: str = os.getenv("USERS_DATABASE_URL", "sqlite+aiosqlite:///./users.db")
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "True").lower() == "true"
    
    # Authentication Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret-key-for-jwt-tokens")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 20))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 1))
    
    # OAuth Settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Email Settings
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@xenx.com")
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", 5242880))  # 5MB in bytes
    
    # Microservices
    CRM_DATABASE_URL: str = os.getenv("CRM_DATABASE_URL", "sqlite+aiosqlite:///./crm.db")
    TAX_PLANNER_DATABASE_URL: str = os.getenv("TAX_PLANNER_DATABASE_URL", "sqlite+aiosqlite:///./tax_planner.db")
    
    # Redis Settings for caching, rate limiting, and session management
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATE_LIMIT_DEFAULT: int = int(os.getenv("RATE_LIMIT_DEFAULT", 100))  # requests per minute
    USE_REDIS_CACHE: bool = os.getenv("USE_REDIS_CACHE", "False").lower() == "true"
    
    # AWS Settings
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "xenx-uploads")
    
    # Security Settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    SSL_ENABLED: bool = os.getenv("SSL_ENABLED", "False").lower() == "true"
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        elif isinstance(v, str):
            return [v]
        raise ValueError(v)
    
    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance to avoid loading from environment
    variables multiple times.
    """
    settings = Settings()
    logger.info(f"Loading settings for environment: {settings.ENVIRONMENT}")
    return settings