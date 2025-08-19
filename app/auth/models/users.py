from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.auth.database import Base
from app.enterprises.models.enterprises import Enterprise
import enum


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
    # role = Column(SQLAEnum(UserRole), nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)
    # is_onboarded = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enterprises = relationship("Enterprise", back_populates="owner")
    staff_profiles = relationship("Staff", back_populates="user_details")
    client_profiles = relationship("Client", back_populates="user_details")

    class Config:
        from_attributes = True

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=False, index=True, nullable=False)
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=False)
    role = Column(SQLAEnum(StaffRole), nullable=False)

    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_details = relationship("User", back_populates="staff_profiles")
    enterprise = relationship("Enterprise", back_populates="staffs")

    def activate(self):
        is_active = True

    def deactivate(self):
        is_active = False
        #XXX after 7 days of being inactive staff needs to be removed
    
    def __str__(self):
        return self.user_details.username

    class Config:
        from_attributes = True
    
    __table_args__ = (
        UniqueConstraint('user_id', 'enterprise_id', name='uq_staff_user_enterprise'),
    )

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=False, index=True, nullable=False)
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=False)

    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_details = relationship("User", back_populates="client_profiles")
    enterprise = relationship("Enterprise", back_populates="clients")


    def activate(self):
        is_active = True

    def deactivate(self):
        is_active = False
        #XXX after 7 days of being inactive client needs to be removed
    
    def __str__(self):
        return self.user_details.username

    class Config:
        from_attributes = True

    __table_args__ = (
        UniqueConstraint('user_id', 'enterprise_id', name='uq_client_user_enterprise'),
    )


