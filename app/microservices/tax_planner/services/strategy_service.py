from typing import Tuple, Optional, List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload
from uuid import UUID
import json

from app.microservices.tax_planner.models.tax_strategies import (
    TaxStrategy, CustomStrategy, ImplementationTask, TaxStrategyType
)
from app.microservices.tax_planner.models.client_goals import ClientGoal, ClientGoalOptions
from app.microservices.tax_planner.models.projects import Project
from app.microservices.tax_planner.schemas.strategy_schemas import (
    ClientGoalsUpdate, ClientGoalsResponse, ClientGoalResponse,
    StrategyCreate, StrategyUpdate, StrategyResponse,
    RecommendedStrategiesResponse, ImplementationTaskCreate
)


class StrategyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Client Goals Methods ---
    async def update_client_goals(
        self, enterprise_id: int, project_id: int, goals_data: ClientGoalsUpdate
    ) -> Tuple[Optional[ClientGoalsResponse], Optional[str]]:
        """Update client goals for a project"""
        # Check if project exists and belongs to the enterprise
        query = select(Project).where(
            Project.id == project_id,
            Project.enterprise_id == enterprise_id
        )
        result = await self.db.execute(query)
        project = result.scalars().first()

        if not project:
            return None, f"Project not found for enterprise {enterprise_id}"

        # Delete existing goals for this project
        delete_query = delete(ClientGoal).where(ClientGoal.project_id == project_id)
        await self.db.execute(delete_query)

        # Create new goals
        goals_response = []
        for goal_option in goals_data.goals:
            # Create a new goal
            new_goal = ClientGoal(
                goal=goal_option,
                project_id=project_id
            )
            self.db.add(new_goal)
            await self.db.flush()  # To get the ID
            
            # Add to response list
            goals_response.append(self._goal_to_response(new_goal))

        await self.db.commit()

        # Create response
        response = ClientGoalsResponse(
            goals=goals_response,
            message=f"Successfully updated {len(goals_response)} goals for project {project_id}"
        )
        
        return response, None

    async def get_recommended_strategies(
        self, enterprise_id: int, project_id: int
    ) -> Tuple[Optional[RecommendedStrategiesResponse], Optional[str]]:
        """Get recommended strategies based on client goals"""
        # Check if project exists and belongs to the enterprise
        query = select(Project).where(
            Project.id == project_id,
            Project.enterprise_id == enterprise_id
        )
        result = await self.db.execute(query)
        project = result.scalars().first()

        if not project:
            return None, f"Project not found for enterprise {enterprise_id}"

        # Get client goals for this project
        goals_query = select(ClientGoal).where(ClientGoal.project_id == project_id)
        goals_result = await self.db.execute(goals_query)
        goals = goals_result.scalars().all()

        if not goals:
            return None, f"No goals found for project {project_id}. Please set client goals first."

        # Get goal types to search for strategies
        goal_types = [goal.goal for goal in goals]

        # Find all system strategies that align with these goals
        # In a real implementation, this would use a more sophisticated matching algorithm
        # For now, we'll just get some system strategies as a demo
        strategy_query = select(TaxStrategy).where(
            TaxStrategy.type == TaxStrategyType.SYSTEM
        ).limit(5)  # Just get a few for demo purposes
        
        strategy_result = await self.db.execute(strategy_query)
        strategies = strategy_result.scalars().all()

        if not strategies:
            return None, "No matching strategies found for the provided goals"

        # Create response
        response = RecommendedStrategiesResponse(
            project_id=project_id,
            strategies=[self._strategy_to_response(strategy) for strategy in strategies],
            goals=[self._goal_to_response(goal) for goal in goals],
            message=f"Found {len(strategies)} recommended strategies based on {len(goals)} client goals"
        )
        
        return response, None

    # --- System Strategy Methods ---
    async def get_system_strategies(self) -> Tuple[Optional[List[StrategyResponse]], Optional[str]]:
        """Get all system tax strategies"""
        query = select(TaxStrategy).where(
            TaxStrategy.type == TaxStrategyType.SYSTEM
        ).options(
            joinedload(TaxStrategy.implementation_tasks)
        )
        
        result = await self.db.execute(query)
        strategies = result.scalars().all()

        if not strategies:
            return [], None  # Empty list, not an error

        return [self._strategy_to_response(strategy) for strategy in strategies], None

    # --- Custom Strategy Methods ---
    async def create_custom_from_system(
        self, enterprise_id: int, system_strategy_id: int, strategy_update: StrategyUpdate
    ) -> Tuple[Optional[StrategyResponse], Optional[str]]:
        """Create a custom strategy for an enterprise using a system strategy as template"""
        # Find the system strategy
        query = select(TaxStrategy).where(
            TaxStrategy.id == system_strategy_id,
            TaxStrategy.type == TaxStrategyType.SYSTEM
        ).options(
            joinedload(TaxStrategy.implementation_tasks)
        )
        
        result = await self.db.execute(query)
        system_strategy = result.scalars().first()

        if not system_strategy:
            return None, f"System strategy with ID {system_strategy_id} not found"

        # Create a new custom strategy based on the system strategy
        custom_strategy = CustomStrategy(
            name=strategy_update.name or system_strategy.name,
            description=strategy_update.description or system_strategy.description,
            eligibility_criteria=strategy_update.eligibility_criteria or system_strategy.eligibility_criteria,
            implementation_fee=strategy_update.implementation_fee or system_strategy.implementation_fee,
            calculation_formula=strategy_update.calculation_formula or system_strategy.calculation_formula,
            relevant_details=strategy_update.relevant_details or system_strategy.relevant_details,
            type=TaxStrategyType.CUSTOM,
            enterprise_id=enterprise_id,
            base_strategy_id=system_strategy_id
        )
        
        self.db.add(custom_strategy)
        await self.db.flush()  # To get the ID

        # Copy implementation tasks if not provided in update
        if not strategy_update.implementation_tasks:
            for task in system_strategy.implementation_tasks:
                new_task = ImplementationTask(
                    strategy_id=custom_strategy.id,
                    description=task.description,
                    status=task.status,
                    due_date=task.due_date
                )
                self.db.add(new_task)
        else:
            # Create new implementation tasks from update
            for task_data in strategy_update.implementation_tasks:
                new_task = ImplementationTask(
                    strategy_id=custom_strategy.id,
                    description=task_data.description,
                    status=task_data.status,
                    due_date=task_data.due_date
                )
                self.db.add(new_task)

        await self.db.commit()
        await self.db.refresh(custom_strategy)
        
        # Reload the strategy with tasks
        query = select(CustomStrategy).where(
            CustomStrategy.id == custom_strategy.id
        ).options(
            joinedload(CustomStrategy.implementation_tasks)
        )
        
        result = await self.db.execute(query)
        refreshed_strategy = result.scalars().first()
        
        return self._strategy_to_response(refreshed_strategy), None

    async def create_custom_strategy(
        self, enterprise_id: int, strategy_data: StrategyCreate
    ) -> Tuple[Optional[StrategyResponse], Optional[str]]:
        """Create a completely new custom strategy for an enterprise"""
        # Create the custom strategy
        custom_strategy = CustomStrategy(
            name=strategy_data.name,
            description=strategy_data.description,
            eligibility_criteria=strategy_data.eligibility_criteria,
            implementation_fee=strategy_data.implementation_fee,
            calculation_formula=strategy_data.calculation_formula,
            relevant_details=strategy_data.relevant_details,
            type=TaxStrategyType.CUSTOM,
            enterprise_id=enterprise_id,
            base_strategy_id=None  # This is a completely new strategy
        )
        
        self.db.add(custom_strategy)
        await self.db.flush()  # To get the ID

        # Create implementation tasks if provided
        if strategy_data.implementation_tasks:
            for task_data in strategy_data.implementation_tasks:
                new_task = ImplementationTask(
                    strategy_id=custom_strategy.id,
                    description=task_data.description,
                    status=task_data.status,
                    due_date=task_data.due_date
                )
                self.db.add(new_task)

        await self.db.commit()
        await self.db.refresh(custom_strategy)
        
        # Reload the strategy with tasks
        query = select(CustomStrategy).where(
            CustomStrategy.id == custom_strategy.id
        ).options(
            joinedload(CustomStrategy.implementation_tasks)
        )
        
        result = await self.db.execute(query)
        refreshed_strategy = result.scalars().first()
        
        return self._strategy_to_response(refreshed_strategy), None

    async def get_all_enterprise_strategies(
        self, enterprise_id: int
    ) -> Tuple[Optional[List[StrategyResponse]], Optional[str]]:
        """Get all strategies available to an enterprise (system + custom)"""
        # Get system strategies
        system_query = select(TaxStrategy).where(
            TaxStrategy.type == TaxStrategyType.SYSTEM
        ).options(
            joinedload(TaxStrategy.implementation_tasks)
        )
        
        system_result = await self.db.execute(system_query)
        system_strategies = system_result.scalars().all()

        # Get custom strategies for this enterprise
        custom_query = select(CustomStrategy).where(
            CustomStrategy.enterprise_id == enterprise_id
        ).options(
            joinedload(CustomStrategy.implementation_tasks)
        )
        
        custom_result = await self.db.execute(custom_query)
        custom_strategies = custom_result.scalars().all()

        # Combine results
        all_strategies = list(system_strategies) + list(custom_strategies)
        
        if not all_strategies:
            return [], None  # Empty list, not an error

        return [self._strategy_to_response(strategy) for strategy in all_strategies], None

    async def get_enterprise_custom_strategies(
        self, enterprise_id: int
    ) -> Tuple[Optional[List[StrategyResponse]], Optional[str]]:
        """Get only the custom strategies created by an enterprise"""
        query = select(CustomStrategy).where(
            CustomStrategy.enterprise_id == enterprise_id
        ).options(
            joinedload(CustomStrategy.implementation_tasks)
        )
        
        result = await self.db.execute(query)
        strategies = result.scalars().all()

        if not strategies:
            return [], None  # Empty list, not an error

        return [self._strategy_to_response(strategy) for strategy in strategies], None

    # --- Helper Methods ---
    def _strategy_to_response(self, strategy: Union[TaxStrategy, CustomStrategy]) -> StrategyResponse:
        """Convert a strategy model to a response schema"""
        # Create a dictionary with all the attributes
        strategy_dict = {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "eligibility_criteria": strategy.eligibility_criteria,
            "implementation_fee": strategy.implementation_fee,
            "calculation_formula": strategy.calculation_formula,
            "relevant_details": strategy.relevant_details,
            "type": strategy.type,
            "created_at": strategy.created_at,
            "updated_at": strategy.updated_at,
            "implementation_tasks": [
                {
                    "id": task.id,
                    "strategy_id": task.strategy_id,
                    "description": task.description,
                    "status": task.status,
                    "due_date": task.due_date,
                    "created_at": task.created_at,
                    "updated_at": task.updated_at
                } for task in strategy.implementation_tasks
            ]
        }
        
        # Add enterprise_id and base_strategy_id for custom strategies
        if hasattr(strategy, 'enterprise_id'):
            strategy_dict["enterprise_id"] = strategy.enterprise_id
        
        if hasattr(strategy, 'base_strategy_id'):
            strategy_dict["base_strategy_id"] = strategy.base_strategy_id
        
        return StrategyResponse.model_validate(strategy_dict)

    def _goal_to_response(self, goal: ClientGoal) -> ClientGoalResponse:
        """Convert a client goal model to a response schema"""
        # Create a dictionary with all the attributes and convert to response model
        goal_dict = {
            "id": goal.id,
            "goal": goal.goal,
            "project_id": goal.project_id,
            "related_strategy_id": goal.related_strategy_id,
            "created_at": goal.created_at,
            "updated_at": goal.updated_at
        }
        return ClientGoalResponse.model_validate(goal_dict)
