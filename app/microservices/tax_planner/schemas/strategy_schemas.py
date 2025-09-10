from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.microservices.tax_planner.models.tax_strategies import TaxStrategyType, TaskStatus


# --- Client Goals Schemas ---
class ClientGoalBase(BaseModel):
    """Base schema for system client goal data"""
    title: str
    description: str


class ClientGoalCreate(ClientGoalBase):
    """Schema for creating a system client goal"""
    pass


class ClientGoalResponse(ClientGoalBase):
    """Schema for system client goal response data"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomGoalBase(BaseModel):
    """Base schema for custom goal data"""
    title: str
    description: str


class CustomGoalCreate(CustomGoalBase):
    """Schema for creating a custom goal"""
    enterprise_id: int


class CustomGoalResponse(CustomGoalBase):
    """Schema for custom goal response data"""
    id: UUID
    enterprise_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GoalSelectionItem(BaseModel):
    """Schema for selecting a goal (either system or custom)"""
    goal_id: Optional[UUID] = None
    custom_goal_id: Optional[UUID] = None
    
    @classmethod
    def model_validate(cls, v):
        if isinstance(v, dict):
            if not v.get('goal_id') and not v.get('custom_goal_id'):
                raise ValueError("Either goal_id or custom_goal_id must be provided")
            if v.get('goal_id') and v.get('custom_goal_id'):
                raise ValueError("Cannot specify both goal_id and custom_goal_id")
        return super().model_validate(v)


class ProjectGoalsUpdate(BaseModel):
    """Schema for updating project goals"""
    goals: List[GoalSelectionItem]


class ProjectGoalResponse(BaseModel):
    """Schema for project goal response data"""
    goal: Optional[ClientGoalResponse] = None
    custom_goal: Optional[CustomGoalResponse] = None

    class Config:
        from_attributes = True


class ProjectGoalsResponse(BaseModel):
    """Schema for project goals response data"""
    project_id: int
    goals: List[ProjectGoalResponse]
    message: str = "Project goals updated successfully"


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
    selected_goals: List[ProjectGoalResponse]
    message: str = "Recommended strategies based on selected goals"
