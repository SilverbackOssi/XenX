from pydantic_settings import BaseSettings
from typing import Any, Dict, List
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Xentoba"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Authentication
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_MINUTES: int = 15
    MFA_ISSUER_NAME: str = "XenX"
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: str = None
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = None
    # REDIS_URL: str = None

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # AWS
    AWS_ACCESS_KEY_ID: str = None
    AWS_SECRET_ACCESS_KEY: str = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = None
    
    class Config:
        env_file = ".env"
        
    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
