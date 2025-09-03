
# system strategies
from sqlalchemy import Enum, Column, DateTime, Integer, String, DECIMAL, Text, func, JSON, ForeignKey
from app.microservices.tax_planner.tp_database import TPBase
from sqlalchemy.orm import relationship
import enum


class TaxStrategyType(enum.Enum):
    SYSTEM = "system"
    CUSTOM = "custom"

class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaxStrategy(TPBase):
    __tablename__ = 'tax_strategies'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(TaxStrategyType), nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    eligibility_criteria = Column(Text, nullable=True) # e.g., "Equipments must be above 50% of business use"

    implementation_fee = Column(DECIMAL(10, 2), nullable=True)
    relevant_details = Column(JSON, nullable=True)
    # implementation_steps = Column(Text, nullable=True)
    
    
    # Savings calculation
    calculation_formula = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    related_goals = relationship("ClientGoal", back_populates="tax_strategy")
    implementation_tasks = relationship("ImplementationTask", back_populates="strategy", cascade="all, delete-orphan")
    tax_plans = relationship("TaxPlan", back_populates="strategy", cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'tax_strategy',
    }

# Custom strategies inherit from TaxStrategy and are stored in the same table.
class CustomStrategy(TaxStrategy):
    __mapper_args__ = {
        'polymorphic_identity': 'custom_strategy',
    }


class ImplementationTask(TPBase):
    __tablename__ = 'implementation_tasks'

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey('tax_strategies.id'), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    due_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True),  server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    strategy = relationship("TaxStrategy", back_populates="implementation_tasks")
    # goal = relationship("ClientGoal", back_populates="implementation_tasks", uselist=False)
