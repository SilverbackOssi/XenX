from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.auth.database import Base
from app.enterprises.models.subscriptions import SubscriptionPlans


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    last_name = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    subscription_plan = Column(SQLAEnum(SubscriptionPlans), default=SubscriptionPlans.FREE, nullable=False)
    google_id = Column(String, unique=True, nullable=True)
    
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)
    otp_code = Column(String, nullable=True)
    otp_code_expires_at = Column(DateTime, nullable=True)
    role = Column(String, default="client")
    token_version = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enterprises = relationship("Enterprise", back_populates="owner")
    staff_profiles = relationship("Staff", back_populates="user_details", foreign_keys="Staff.user_id")
    client_profiles = relationship("Client", back_populates="user_details", foreign_keys="Client.user_id")
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=True)
    enterprise = relationship("Enterprise", back_populates="staffs")

    # A relationship for staff members where this user is the inviter
    invited_staffs = relationship("Staff", back_populates="inviter", foreign_keys="Staff.inviter_id")
    invited_clients = relationship("Client", back_populates="inviter", foreign_keys="Client.inviter_id")

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False
    
    def __str__(self):
        return self.username or self.email
    
    class Config:
        from_attributes = True

