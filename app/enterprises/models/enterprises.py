from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.auth.database import Base
import enum

class EnterpriseType(enum.Enum):
    BUSINESS = "business"
    NON_PROFIT = "non-profit"
    GOVERNMENT = "government"

class Enterprise(Base):
    __tablename__ = "enterprises"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, unique=True, index=True)
    email = Column(String, nullable=False)
    type = Column(SQLAEnum(EnterpriseType), nullable=False)
    default_tax_year = Column(Integer, nullable=False)
    
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
