
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.microservices.tax_planner.tp_database import get_db
from app.microservices.tax_planner.schemas.strategy_schemas import (
    StrategyResponse, StrategyCreate, StrategyUpdate,
    RecommendedStrategiesResponse
)
from app.microservices.tax_planner.services.strategy_service import StrategyService
from app.auth.services.token_service import TokenService
from app.auth.models.users import User

strategy_router = APIRouter(prefix="/tentants", tags=["Tax Strategies"])

# --- Strategy Recommendations Endpoint ---
@strategy_router.get(
    "/{enterprise_id}/projects/{project_id}/recommended-strategies", 
    response_model=RecommendedStrategiesResponse, 
    status_code=status.HTTP_200_OK,
    summary="Get recommended strategies based on client goals"
)
async def get_recommended_strategies(
    enterprise_id: int, 
    project_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    Get recommended tax strategies based on the saved client goals for a project.
    Returns an error if no goals have been saved for the project.
    """
    strategy_service = StrategyService(db)
    recommendations, error = await strategy_service.get_recommended_strategies(
        enterprise_id, project_id
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in error.lower() 
            else status.HTTP_400_BAD_REQUEST,
            detail=error
        )
        
    return recommendations


# --- System Strategy Endpoints ---
@strategy_router.get(
    "/system-strategies", 
    response_model=List[StrategyResponse], 
    status_code=status.HTTP_200_OK,
    summary="Get all system tax strategies"
)
async def get_system_strategies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    Get all system-defined tax strategies available to all enterprises.
    These are pre-defined strategies that serve as templates.
    """
    strategy_service = StrategyService(db)
    strategies, error = await strategy_service.get_system_strategies()
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
        
    return strategies

# --- Enterprise Custom Strategy Endpoints ---
@strategy_router.post(
    "/{enterprise_id}/strategies/from-system/{system_strategy_id}", 
    response_model=StrategyResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create custom strategy from system template"
)
async def create_custom_strategy_from_system(
    enterprise_id: int, 
    system_strategy_id: int, 
    strategy_update: StrategyUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    Create a custom tax strategy for an enterprise using a system strategy as a template.
    The strategy can be customized with enterprise-specific details.
    """
    strategy_service = StrategyService(db)
    custom_strategy, error = await strategy_service.create_custom_from_system(
        enterprise_id, system_strategy_id, strategy_update
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in error.lower() 
            else status.HTTP_400_BAD_REQUEST,
            detail=error
        )
        
    return custom_strategy

@strategy_router.post(
    "/{enterprise_id}/strategies", 
    response_model=StrategyResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new custom strategy for an enterprise"
)
async def create_custom_strategy(
    enterprise_id: int, 
    strategy_data: StrategyCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    Create a completely new custom tax strategy for an enterprise.
    This allows enterprises to define their own unique strategies.
    """
    strategy_service = StrategyService(db)
    strategy, error = await strategy_service.create_custom_strategy(
        enterprise_id, strategy_data
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
        
    return strategy

@strategy_router.get(
    "/{enterprise_id}/strategies", 
    response_model=List[StrategyResponse], 
    status_code=status.HTTP_200_OK,
    summary="Get all strategies available to an enterprise"
)
async def get_all_enterprise_strategies(
    enterprise_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    Get all tax strategies available to an enterprise.
    Includes both system strategies and custom strategies created by the enterprise.
    """
    strategy_service = StrategyService(db)
    strategies, error = await strategy_service.get_all_enterprise_strategies(
        enterprise_id
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in error.lower() 
            else status.HTTP_400_BAD_REQUEST,
            detail=error
        )
        
    return strategies

@strategy_router.get(
    "/{enterprise_id}/custom-strategies", 
    response_model=List[StrategyResponse], 
    status_code=status.HTTP_200_OK,
    summary="Get only custom strategies created by an enterprise"
)
async def get_enterprise_custom_strategies(
    enterprise_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(TokenService.get_current_user)
):
    """
    Get only the custom tax strategies created by a specific enterprise.
    Does not include system strategies.
    """
    strategy_service = StrategyService(db)
    strategies, error = await strategy_service.get_enterprise_custom_strategies(
        enterprise_id
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in error.lower() 
            else status.HTTP_400_BAD_REQUEST,
            detail=error
        )
        
    return strategies
