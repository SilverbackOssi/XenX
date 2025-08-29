from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.microservices.tax_planner.tp_database import TPBase

class TaxEntity(TPBase):
    __tablename__ = "tax_entities"

    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String, nullable=True)
    jurisdiction = Column(String, nullable=True)
    filing_status = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    entity_type = Column(String, nullable=True)
    default_tax_year = Column(String, nullable=True)
    additional_notes = Column(Text, nullable=True)
    verification_doc_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="tax_entity", uselist=False)

class Project(TPBase):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    enterprise_id = Column(Integer, nullable=False)  # No ForeignKey here, enterprises exist in a separate DB
    tax_entity_id = Column(Integer, ForeignKey("tax_entities.id"), unique=True, nullable=False)
    project_name = Column(String, nullable=False)
    client_name = Column(String, nullable=True)
    client_phone_number = Column(String, nullable=True)
    client_email = Column(String, nullable=True)
    project_type = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tax_entity = relationship("TaxEntity", back_populates="project", uselist=False)