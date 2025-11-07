from sqlalchemy import String, Boolean, UniqueConstraint, Column, Integer, ForeignKey, DateTime, Enum, func, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.microservices.tax_planner.tp_database import TPBase
import enum


class ClientGoal(TPBase):
    """System-defined client goals"""
    __tablename__ = 'client_goals'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ClientGoal(title='{self.title}', description='{self.description}')>"


class CustomGoal(TPBase):
    """Enterprise-specific custom goals"""
    __tablename__ = 'custom_goals'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enterprise_id = Column(Integer, nullable=False)  # No FK as enterprises are in different DB
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<CustomGoal(enterprise_id={self.enterprise_id}, title='{self.title}')>"

