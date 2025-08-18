from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAEnum
from app.auth.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CPA = "cpa"
    CLIENT = "client"
    STAFF = "staff"

class StaffRole(str, enum.Enum):
    ASSISTANT = "assistant"
    CPA = "cpa"
    REVIEWER = "reviewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    last_name = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    role = Column(SQLAEnum(UserRole), nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    email_verified = Column(Boolean, default=False)
    is_onboarded = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
