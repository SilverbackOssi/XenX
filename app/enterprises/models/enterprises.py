from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.auth.database import Base
import enum

class Enterprise(Base):
    __tablename__ = "enterprises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to the User model
    owner = relationship("User", back_populates="enterprises")
    staffs = relationship("Staff", back_populates="enterprise")
    clients = relationship("Client", back_populates="enterprise")

    class Config:
        from_attributes = True
