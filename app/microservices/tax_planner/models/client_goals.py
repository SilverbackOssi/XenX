from sqlalchemy import UniqueConstraint, Column, Integer, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.microservices.tax_planner.tp_database import TPBase
import enum

# I dont think this should be hard coded, create endpoint to add and remove goals
class ClientGoalOptions(str, enum.Enum):
   OPTIMIZE_QUARTERLY_TAXES = "optimize quarterly taxes"
   INCREASE_CASH_SAVINGS = "increase cash savings"
   MAXIMIZE_TAX_SAVINGS = "maximize tax savings"
   REDUCE_DEBT = "reduce debt"
   ENSURE_COMPLIANCE = "ensure compliance"
   ENSURE_AUDITPROOF = "ensure audit-proof"
   GIFTING_FAMILY_MEMBERS = "gifting family members"
   SAVE_FOR_RETIREMENT = "save for retirement"


class ClientGoal(TPBase):
    __tablename__ = 'client_goals'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal = Column(Enum(ClientGoalOptions), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    related_strategy_id = Column(Integer, ForeignKey('tax_strategies.id'), nullable=True)

    created_at = Column(DateTime(timezone=True),  server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="goals", uselist=False)
    tax_strategy = relationship("TaxStrategy", back_populates="related_goals", uselist=True)

    # unique constraint on project_id and goal
    __table_args__ = (UniqueConstraint('project_id', 'goal', name='uq_project_goal'),)

    def __repr__(self):
        return f"<ClientGoal(goal='{self.goal}')>"

