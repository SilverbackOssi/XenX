from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.microservices.tax_planner.tp_database import get_db
from app.microservices.tax_planner.schemas.strategy_schemas import (
	ClientGoalsUpdate, ClientGoalsResponse
)
from app.microservices.tax_planner.services.strategy_service import StrategyService
from app.auth.services.token_service import TokenService
from app.auth.models.users import User
from app.microservices.tax_planner.models.client_goals import ClientGoalOptions

client_goal_router = APIRouter(prefix="/enterprises", tags=["Client Goals"])

# --- Client Goals Endpoints ---
@client_goal_router.put(
	"/{enterprise_id}/projects/{project_id}/goals",
	response_model=ClientGoalsResponse,
	status_code=status.HTTP_200_OK,
	summary="Update client goals for a project"
)
async def update_client_goals(
	enterprise_id: int,
	project_id: int,
	goals_data: ClientGoalsUpdate,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(TokenService.get_current_user)
):
	"""
	Update tax planning goals for a specific client project.
	These goals will be used to recommend appropriate tax strategies.
	"""
	strategy_service = StrategyService(db)
	updated_goals, error = await strategy_service.update_client_goals(
		enterprise_id, project_id, goals_data
	)
	if error:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND if "not found" in error.lower()
			else status.HTTP_400_BAD_REQUEST,
			detail=error
		)
	return updated_goals

# --- System Client Goals Endpoint ---
@client_goal_router.get(
	"/system-client-goals",
	response_model=List[str],
	status_code=status.HTTP_200_OK,
	summary="Get all available client goals from the system"
)
async def get_all_system_client_goals():
	"""
	Get all available client goals defined in the system.
	"""
	return [goal.value for goal in ClientGoalOptions]
