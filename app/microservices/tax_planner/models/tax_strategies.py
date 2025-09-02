
# system strategies
from sqlalchemy import Column, DateTime, Integer, String, DECIMAL, Text, func
from app.microservices.tax_planner.tp_database import TPBase


class TaxStrategy(TPBase):
    __tablename__ = 'tax_strategies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    eligibility_criteria = Column(Text, nullable=True)

    implementation_fee = Column(DECIMAL(10, 2), nullable=True)
    # implementation_steps = Column(Text, nullable=True)
    
    
    # Savings calculation
    calculation_formula = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    related_goals = relationship("ClientGoal", back_populates="tax_strategy")


# custom strategies, copy from system strategies per enterprise
# relevant_details = Column(Text, nullable=True)