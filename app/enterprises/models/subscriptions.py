from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, Enum as SQLAEnum
from app.auth.database import Base

# class PlanType(str, enum.Enum):
#     FREE = "free"
#     PRO = "pro"
#     BUSINESS = "business"


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    features = Column(Text, nullable=True)  # e.g., JSON string or comma-separated
    user_limit = Column(Integer, nullable=True)
    storage_limit_gb = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return self.name 

    class Config:
        from_attributes = True
