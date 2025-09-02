from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.microservices.tax_planner.tp_database import TPBase
import enum


class ClientGoalOptions(str, enum.Enum):
   OPTIMIZE_QUARTERLY_TAXES = "optimize quarterly taxes"
   INCREASE_CASH_SAVINGS = "increase cash savings"
   MAXIMIZE_TAX_SAVINGS = "maximize tax savings"
   REDUCE_DEBT = "reduce debt"
   ENSURE_COMPLIANCE = "ensure compliance"
   ENSURE_AUDITPROOF = "ensure audit-proof"
   GIFTING_FAMILY_MEMBERS = "gifting family members"
   SAVE_FOR_KIDS_RETIREMENT = "save for kids retirement"


class ClientGoal(TPBase):
    __tablename__ = 'client_goals'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal = Column(Enum(ClientGoalOptions), nullable=False)
    
    created_at = Column(DateTime(timezone=True),  server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project_client_goals = relationship("ProjectClientGoal", back_populates="goal", cascade="all, delete-orphan")
    tax_strategy = relationship("TaxStrategy", back_populates="related_goals", uselist=True)

    def __repr__(self):
        return f"<ClientGoal(goal='{self.goal}')>"

class ProjectClientGoal(TPBase):
    __tablename__ = 'project_client_goals'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey('client_goals.id'), nullable=False)

    created_at = Column(DateTime(timezone=True),  server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="client_goals")
    goal = relationship("ClientGoal", back_populates="project_client_goals")
