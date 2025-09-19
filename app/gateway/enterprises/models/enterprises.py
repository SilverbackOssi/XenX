from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Session
from app.gateway.auth.database import Base
from .permissions import StaffPermission, StaffRole
import enum

class EnterpriseType(enum.Enum):
    ACCOUNTING = "accounting"
    TAX_ADVISORY = "tax-advisory"
    CONSULTING = "consulting"
    BOOKKEEPING = "bookkeeping"
    OTHER = "other"

# (CPA firm)
class Enterprise(Base):
    __tablename__ = "enterprises"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, unique=True, index=True)
    email = Column(String, nullable=False)
    type = Column(SQLAEnum(EnterpriseType), nullable=False, default=EnterpriseType.TAX_ADVISORY)
    tax_year = Column(Integer, nullable=False)
    
    description = Column(String, nullable=True)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    address = Column(String, nullable=True)
    website = Column(String, nullable=True)

    # Branding
    logo_url = Column(String, nullable=True)  # URL or path to the logo image
    primary_color = Column(String, nullable=True)  # Hex code for the primary brand color
    accent_color = Column(String, nullable=True)  # Hex code for the accent brand color
    footer_text = Column(String, nullable=True)  # Text to display in the footer of exported documents

    # Status & Timestamps
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to the User model
    owner = relationship("User", back_populates="enterprises")
    staffs = relationship("Staff", back_populates="enterprise")
    clients = relationship("Client", back_populates="enterprise")

    class Config:
        from_attributes = True

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=False, index=True, nullable=False)
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=False)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    invite_token = Column(String, nullable=True)
    invite_token_expires_at = Column(DateTime, nullable=True)
    role = Column(SQLAEnum(StaffRole), nullable=False)
    permission = Column(SQLAEnum(StaffPermission), nullable=False, default=StaffPermission.VIEW_ONLY)

    # Add Permissions

    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships 
    user_details = relationship("User", back_populates="staff_profiles", foreign_keys=[user_id])
    enterprise = relationship("Enterprise", back_populates="staffs")
    inviter = relationship("User", back_populates="invited_staffs", foreign_keys=[inviter_id])
    
    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False
        # TODO: Implement a background task to remove inactive staff after 7 days.

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
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_details = relationship("User", back_populates="client_profiles", foreign_keys=[user_id])
    enterprise = relationship("Enterprise", back_populates="clients")

    inviter = relationship("User", back_populates="invited_clients", foreign_keys=[inviter_id])

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False
        # TODO: Implement a background task to remove inactive clients after 7 days.

    def __str__(self):
        return self.user_details.username

    class Config:
        from_attributes = True

    __table_args__ = (
        UniqueConstraint('user_id', 'enterprise_id', name='uq_client_user_enterprise'),
    )
