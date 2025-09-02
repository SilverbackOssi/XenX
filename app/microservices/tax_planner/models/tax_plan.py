

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.microservices.tax_planner.tp_database import TPBase

class TaxPlan(TPBase):
    __tablename__ = 'tax_plans'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    strategy_id = Column(Integer, ForeignKey('tax_strategies.id'))
    
    start_date = Column(Date)
    end_date = Column(Date)
    
    projected_savings = Column(Float)
    status = Column(String) # e.g., 'Draft', 'Active', 'Completed'

    # Relationships
    project = relationship("Project", back_populates="tax_plan")
    strategy = relationship("TaxStrategy", back_populates="tax_plans")
