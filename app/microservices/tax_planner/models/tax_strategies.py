
from sqlalchemy import Enum, Column, DateTime, Integer, String, DECIMAL, Text, func, JSON, ForeignKey
from app.microservices.tax_planner.tp_database import TPBase
from sqlalchemy.orm import relationship
import enum


class TaxStrategyType(str, enum.Enum):
    SYSTEM = "system"
    CUSTOM = "custom"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaxStrategy(TPBase):
    __tablename__ = 'tax_strategies'

    id = Column(Integer, primary_key=True, index=True)
    
    type = Column(Enum(TaxStrategyType), nullable=False)

    name = Column(String, nullable=False)
    
    # description: Provides a detailed explanation of the tax strategy.
    # Expected format: Plain text summarizing the strategy's purpose, scope, and any important notes.
    # Usage: Use this field to describe what the strategy entails and how it benefits the client.
    description = Column(Text, nullable=False)

    # eligibility_criteria: Provide a description of the requirements for this strategy.
    # Example: "Equipments must be above 50% of business use"
    # Expected format: Plain text describing specific conditions or prerequisites for eligibility.
    eligibility_criteria = Column(Text, nullable=True)

    implementation_fee = Column(DECIMAL(10, 2), nullable=True)

    # relevant_details: Stores additional information relevant to the tax strategy.
    # Expected format: JSON object containing key-value pairs such as {'industry': 'retail', 'region': 'US', 'notes': 'Requires CPA review'}.
    # Usage: Use this field to store structured data that supplements the strategy, such as industry-specific parameters or custom notes.
    relevant_details = Column(JSON, nullable=True)
    
    # calculation_formula: Stores the formula used to calculate potential savings for this strategy.
    # Expected format: Plain text or expression syntax (e.g., Python expression, SQL, or other supported formats).
    # Usage: This field should contain a valid formula that can be parsed and evaluated by the application logic.
    calculation_formula = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    related_goals = relationship("ClientGoal", back_populates="tax_strategy")
    implementation_tasks = relationship("ImplementationTask", back_populates="strategy", cascade="all, delete-orphan")
    tax_plans = relationship("TaxPlan", back_populates="strategy", cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'tax_strategy',
    }

    def __repr__(self):
        return f"<TaxStrategy(id={self.id}, name={self.name})>"

    def save(self, session):
        """
        Persists the current object to the database using the provided session.
        Usage: Pass an active SQLAlchemy session as the argument.
        """
        session.add(self)
        session.commit()
        session.refresh(self)

# Custom strategies inherit from TaxStrategy and are stored in the same table.
class CustomStrategy(TaxStrategy):

    # Links a custom strategy to its originating base (system) strategy, allowing reference to the base strategy from which it was derived.
    # Usage: Access the base strategy for a given custom strategy via the 'base_strategy' attribute.
    base_strategy_id = Column(Integer, ForeignKey('tax_strategies.id'), nullable=True)

    enterprise_id = Column(Integer, nullable=False) # Non foreign key, just a reference,  enterprises exist in a separate DB

    # Relationships
    base_strategy = relationship("TaxStrategy", backref="custom_strategies", uselist=False, foreign_keys=[base_strategy_id])

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
    # goal = relationship("ClientGoal", back_populates="implementation_tasks", uselist=False) XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
