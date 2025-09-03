from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.microservices.tax_planner.models.client_goals import ClientGoalOptions
from app.microservices.tax_planner.models.tax_strategies import TaxStrategyType, TaskStatus


# --- Client Goals Schemas ---
class ClientGoalsUpdate(BaseModel):
    """Schema for updating client goals for a project"""
    goals: List[ClientGoalOptions]
    

class ClientGoalBase(BaseModel):
    """Base schema for client goal data"""
    goal: ClientGoalOptions
    project_id: int


class ClientGoalCreate(ClientGoalBase):
    """Schema for creating a client goal"""
    pass


class ClientGoalResponse(ClientGoalBase):
    """Schema for client goal response data"""
    id: UUID
    related_strategy_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClientGoalsResponse(BaseModel):
    """Schema for multiple client goals response data"""
    goals: List[ClientGoalResponse]
    message: str = "Client goals updated successfully"


# --- Strategy Schemas ---
class ImplementationTaskBase(BaseModel):
    """Base schema for implementation task data"""
    description: str
    due_date: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING


class ImplementationTaskCreate(ImplementationTaskBase):
    """Schema for creating an implementation task"""
    pass


class ImplementationTaskUpdate(BaseModel):
    """Schema for updating an implementation task"""
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None


class ImplementationTaskResponse(ImplementationTaskBase):
    """Schema for implementation task response data"""
    id: int
    strategy_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StrategyBase(BaseModel):
    """Base schema for tax strategy data"""
    name: str
    description: str
    eligibility_criteria: Optional[str] = None
    implementation_fee: Optional[Decimal] = None
    calculation_formula: str
    relevant_details: Optional[Dict[str, Any]] = None


class StrategyCreate(StrategyBase):
    """Schema for creating a custom tax strategy"""
    implementation_tasks: Optional[List[ImplementationTaskCreate]] = None


class StrategyUpdate(BaseModel):
    """Schema for updating a tax strategy"""
    name: Optional[str] = None
    description: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    implementation_fee: Optional[Decimal] = None
    calculation_formula: Optional[str] = None
    relevant_details: Optional[Dict[str, Any]] = None
    implementation_tasks: Optional[List[ImplementationTaskCreate]] = None


class StrategyResponse(StrategyBase):
    """Schema for tax strategy response data"""
    id: int
    type: TaxStrategyType
    enterprise_id: Optional[int] = None  # Only for custom strategies
    base_strategy_id: Optional[int] = None  # Only for custom strategies derived from system
    implementation_tasks: List[ImplementationTaskResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecommendedStrategiesResponse(BaseModel):
    """Schema for recommended strategies response data"""
    project_id: int
    strategies: List[StrategyResponse]
    goals: List[ClientGoalResponse]
    message: str = "Recommended strategies based on client goals"
