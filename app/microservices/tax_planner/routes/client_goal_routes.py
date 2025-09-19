from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.microservices.tax_planner.tp_database import get_db
from app.microservices.tax_planner.schemas.strategy_schemas import (
	ProjectGoalsUpdate, ProjectGoalsResponse, ProjectGoalResponse, 
	ClientGoalResponse, CustomGoalResponse, CustomGoalCreate
)
from app.microservices.tax_planner.services.strategy_service import StrategyService
from app.gateway.auth.services.token_service import TokenService
from app.gateway.auth.models.users import User

client_goal_router = APIRouter(prefix="/enterprises", tags=["Client Goals"])

# --- Project Goals Endpoints ---
@client_goal_router.put(
	"/{enterprise_id}/projects/{project_id}/goals",
	response_model=ProjectGoalsResponse,
	status_code=status.HTTP_200_OK,
	summary="Update project goals"
)
async def update_project_goals(
	enterprise_id: int,
	project_id: int,
	goals_data: ProjectGoalsUpdate,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(TokenService.get_current_user)
):
	"""
	Update goals for a specific project.
	Users can select both system goals and custom goals from their enterprise.
	"""
	strategy_service = StrategyService(db)
	updated_goals, error = await strategy_service.update_project_goals(
		enterprise_id, project_id, goals_data
	)
	if error:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND if "not found" in error.lower()
			else status.HTTP_400_BAD_REQUEST,
			detail=error
		)
	return updated_goals

@client_goal_router.get(
	"/{enterprise_id}/projects/{project_id}/goals",
	response_model=List[ProjectGoalResponse],
	status_code=status.HTTP_200_OK,
	summary="Get project goals"
)
async def get_project_goals(
	enterprise_id: int,
	project_id: int,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(TokenService.get_current_user)
):
	"""
	Get all goals selected for a specific project.
	"""
	strategy_service = StrategyService(db)
	goals, error = await strategy_service.get_project_goals(enterprise_id, project_id)
	if error:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND if "not found" in error.lower()
			else status.HTTP_400_BAD_REQUEST,
			detail=error
		)
	return goals

# --- System Goals Endpoints ---
@client_goal_router.get(
	"/system-client-goals",
	response_model=List[ClientGoalResponse],
	status_code=status.HTTP_200_OK,
	summary="Get all system client goals"
)
async def get_system_client_goals(
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(TokenService.get_current_user)
):
	"""
	Get all available system-defined client goals.
	"""
	strategy_service = StrategyService(db)
	goals, error = await strategy_service.get_system_client_goals()
	if error:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=error
		)
	return goals

# --- Custom Goals Endpoints ---
@client_goal_router.get(
	"/{enterprise_id}/custom-goals",
	response_model=List[CustomGoalResponse],
	status_code=status.HTTP_200_OK,
	summary="Get enterprise custom goals"
)
async def get_enterprise_custom_goals(
	enterprise_id: int,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(TokenService.get_current_user)
):
	"""
	Get all custom goals created by an enterprise.
	"""
	strategy_service = StrategyService(db)
	goals, error = await strategy_service.get_enterprise_custom_goals(enterprise_id)
	if error:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=error
		)
	return goals

@client_goal_router.post(
	"/{enterprise_id}/custom-goals",
	response_model=CustomGoalResponse,
	status_code=status.HTTP_201_CREATED,
	summary="Create custom goal"
)
async def create_custom_goal(
	enterprise_id: int,
	goal_data: CustomGoalCreate,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(TokenService.get_current_user)
):
	"""
	Create a new custom goal for an enterprise.
	"""
	strategy_service = StrategyService(db)
	goal, error = await strategy_service.create_custom_goal(enterprise_id, goal_data)
	if error:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=error
		)
	return goal
