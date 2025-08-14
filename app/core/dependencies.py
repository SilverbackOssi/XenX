from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from redis import Redis
from typing import Generator

from app.database import SessionLocal
from app.auth.services.auth_service import AuthService
from app.core.config import settings

# Redis connection
redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)
# redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_redis() -> Redis:
    return redis

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    auth_service = AuthService(db, redis)
    email = auth_service.verify_token(token)
    user = auth_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
