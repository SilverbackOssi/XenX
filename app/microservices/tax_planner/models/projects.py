from sqlalchemy import Column, Enum, Integer, String, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.microservices.tax_planner.tp_database import TPBase
import enum

class ProjectType(enum.Enum):
    TAX_PLANNING = "Tax Planning"
    OTHER = "Other"

class EntityType(enum.Enum):
    INDIVIDUAL = "Individual"
    SOLE_PROPRIETORSHIP = "Sole Proprietorship"
    PARTNERSHIP = "Partnership"
    C_CORPORATION = "C Corporation"
    S_CORPORATION = "S Corporation"
    LLC = "Limited Liability Company"

class FilingStatus(enum.Enum):
    SINGLE = "Single"
    MARRIED_FILING_JOINTLY = "Married Filing Jointly"
    MARRIED_FILING_SEPARATELY = "Married Filing Separately"
    HEAD_OF_HOUSEHOLD = "Head of Household"
    QUALIFYING_SURVIVING_SPOUSE = "Qualifying Surviving Spouse"
    QUALIFYING_WIDOWER = "Qualifying Widower"
    QUALIFYING_CHILD = "Qualifying Child"
    OTHER = "Other"

class TaxEntity(TPBase):
    '''Tax content and jurisdiction of a project'''
    __tablename__ = "tax_entities"

    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String, nullable=False)
    jurisdiction = Column(String, nullable=False)
    filing_status = Column(Enum(FilingStatus), nullable=True, default=FilingStatus.SINGLE)
    currency = Column(String, nullable=False, default="USD")
    entity_type = Column(Enum(EntityType), nullable=False)
    tax_year = Column(String, nullable=False)
    additional_notes = Column(Text, nullable=True)
    tax_return_doc_url = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="tax_entity", uselist=False)

class Project(TPBase):
    '''Project details and associated tax entity'''
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    enterprise_id = Column(Integer, nullable=False)  # No ForeignKey here, enterprises exist in a separate DB
    
    tax_entity_id = Column(Integer, ForeignKey("tax_entities.id"), unique=True, nullable=False)
    project_name = Column(String, nullable=False)
    client_name = Column(String, nullable=True)
    client_phone_number = Column(String, nullable=True)
    client_email = Column(String, nullable=True)
    project_type = Column(Enum(ProjectType), nullable=False, default=ProjectType.TAX_PLANNING)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tax_entity = relationship("TaxEntity", back_populates="project", uselist=False)
    project_goals = relationship("ProjectGoal", cascade="all, delete-orphan")


# Association table for project-goal relationships
class ProjectGoal(TPBase):
    """Association table linking projects to selected goals"""
    __tablename__ = 'project_goals'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey('client_goals.id'), nullable=True)
    custom_goal_id = Column(UUID(as_uuid=True), ForeignKey('custom_goals.id'), nullable=True)

    # Ensure either goal_id or custom_goal_id is set, but not both
    __table_args__ = (
        UniqueConstraint('project_id', 'goal_id', name='uq_project_goal'),
        UniqueConstraint('project_id', 'custom_goal_id', name='uq_project_custom_goal'),
    )

    def __repr__(self):
        return f"<ProjectGoal(project_id={self.project_id}, goal_id={self.goal_id}, custom_goal_id={self.custom_goal_id})>"