from typing import Tuple, Optional, List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, and_
from sqlalchemy.orm import joinedload
from uuid import UUID
import json

from app.microservices.tax_planner.models.tax_strategies import (
    TaxStrategy, CustomStrategy, ImplementationTask, TaxStrategyType, StrategyGoal
)
from app.microservices.tax_planner.models.client_goals import (
    ClientGoal, CustomGoal
)
from app.microservices.tax_planner.models.projects import Project, ProjectGoal
from app.microservices.tax_planner.schemas.strategy_schemas import (
    ProjectGoalsUpdate, ProjectGoalsResponse, ProjectGoalResponse,
    ClientGoalResponse, CustomGoalResponse, CustomGoalCreate,
    StrategyCreate, StrategyUpdate, StrategyResponse,
    RecommendedStrategiesResponse, ImplementationTaskCreate
)


class StrategyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Project Goals Methods ---
    async def update_project_goals(
        self, enterprise_id: int, project_id: int, goals_data: ProjectGoalsUpdate
    ) -> Tuple[Optional[ProjectGoalsResponse], Optional[str]]:
        """Update goals for a project"""
        # Check if project exists and belongs to the enterprise
        query = select(Project).where(
            Project.id == project_id,
            Project.enterprise_id == enterprise_id
        )
        result = await self.db.execute(query)
        project = result.scalars().first()

        if not project:
            return None, f"Project not found for enterprise {enterprise_id}"

        # Delete existing project goals
        delete_query = delete(ProjectGoal).where(ProjectGoal.project_id == project_id)
        await self.db.execute(delete_query)

        # Create new project goals
        project_goals = []
        for goal_selection in goals_data.goals:
            new_project_goal = ProjectGoal(
                project_id=project_id,
                goal_id=goal_selection.goal_id,
                custom_goal_id=goal_selection.custom_goal_id
            )
            self.db.add(new_project_goal)
            await self.db.flush()
            project_goals.append(new_project_goal)

        await self.db.commit()

        # Get the goals with their details for response
        response_goals = await self._get_project_goals_with_details(project_id)
        
        response = ProjectGoalsResponse(
            project_id=project_id,
            goals=response_goals,
            message=f"Successfully updated {len(project_goals)} goals for project {project_id}"
        )
        
        return response, None

    async def get_project_goals(
        self, enterprise_id: int, project_id: int
    ) -> Tuple[Optional[List[ProjectGoalResponse]], Optional[str]]:
        """Get all goals for a specific project"""
        # Check if project exists and belongs to the enterprise
        query = select(Project).where(
            Project.id == project_id,
            Project.enterprise_id == enterprise_id
        )
        result = await self.db.execute(query)
        project = result.scalars().first()

        if not project:
            return None, f"Project not found for enterprise {enterprise_id}"

        # Get project goals with details
        response_goals = await self._get_project_goals_with_details(project_id)
        return response_goals, None

    async def get_system_client_goals(self) -> Tuple[Optional[List[ClientGoalResponse]], Optional[str]]:
        """Get all system-defined client goals"""
        query = select(ClientGoal)
        result = await self.db.execute(query)
        goals = result.scalars().all()

        return [self._client_goal_to_response(goal) for goal in goals], None

    async def get_enterprise_custom_goals(
        self, enterprise_id: int
    ) -> Tuple[Optional[List[CustomGoalResponse]], Optional[str]]:
        """Get all custom goals for an enterprise"""
        query = select(CustomGoal).where(CustomGoal.enterprise_id == enterprise_id)
        result = await self.db.execute(query)
        goals = result.scalars().all()

        return [self._custom_goal_to_response(goal) for goal in goals], None

    async def create_custom_goal(
        self, enterprise_id: int, goal_data: CustomGoalCreate
    ) -> Tuple[Optional[CustomGoalResponse], Optional[str]]:
        """Create a new custom goal for an enterprise"""
        new_goal = CustomGoal(
            enterprise_id=enterprise_id,
            title=goal_data.title,
            description=goal_data.description
        )
        
        self.db.add(new_goal)
        await self.db.commit()
        await self.db.refresh(new_goal)
        
        return self._custom_goal_to_response(new_goal), None

    async def get_recommended_strategies(
        self, enterprise_id: int, project_id: int
    ) -> Tuple[Optional[RecommendedStrategiesResponse], Optional[str]]:
        """Get recommended strategies based on project goals"""
        # Check if project exists and belongs to the enterprise
        query = select(Project).where(
            Project.id == project_id,
            Project.enterprise_id == enterprise_id
        )
        result = await self.db.execute(query)
        project = result.scalars().first()

        if not project:
            return None, f"Project not found for enterprise {enterprise_id}"

        # Get project goals
        project_goals = await self._get_project_goals_with_details(project_id)
        if not project_goals:
            return None, f"No goals found for project {project_id}. Please select project goals first."

        # Get all goal IDs (both system and custom)
        system_goal_ids = [pg.goal.id for pg in project_goals if pg.goal]
        custom_goal_ids = [pg.custom_goal.id for pg in project_goals if pg.custom_goal]

        # Find strategies that support ANY of these goals
        strategy_conditions = []
        if system_goal_ids:
            strategy_conditions.append(StrategyGoal.goal_id.in_(system_goal_ids))
        if custom_goal_ids:
            strategy_conditions.append(StrategyGoal.custom_goal_id.in_(custom_goal_ids))
        
        if not strategy_conditions:
            return None, "No valid goals found for recommendation"
            
        strategy_query = select(TaxStrategy).join(StrategyGoal).where(
            or_(*strategy_conditions)
        ).distinct().options(
            joinedload(TaxStrategy.implementation_tasks)
        )
        
        strategy_result = await self.db.execute(strategy_query)
        strategies = strategy_result.scalars().all()

        if not strategies:
            return None, "No matching strategies found for the selected goals"

        # Create response
        response = RecommendedStrategiesResponse(
            project_id=project_id,
            strategies=[self._strategy_to_response(strategy) for strategy in strategies],
            selected_goals=project_goals,
            message=f"Found {len(strategies)} recommended strategies based on {len(project_goals)} selected goals"
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

    async def _get_project_goals_with_details(self, project_id: int) -> List[ProjectGoalResponse]:
        """Helper method to get project goals with their details"""
        # Get project goals
        project_goals_query = select(ProjectGoal).where(ProjectGoal.project_id == project_id)
        project_goals_result = await self.db.execute(project_goals_query)
        project_goals = project_goals_result.scalars().all()

        response_goals = []
        for pg in project_goals:
            goal_response = ProjectGoalResponse()
            
            if pg.goal_id is not None:
                # Get system goal details
                goal_query = select(ClientGoal).where(ClientGoal.id == pg.goal_id)
                goal_result = await self.db.execute(goal_query)
                goal = goal_result.scalars().first()
                if goal:
                    goal_response.goal = self._client_goal_to_response(goal)
            
            if pg.custom_goal_id is not None:
                # Get custom goal details
                custom_goal_query = select(CustomGoal).where(CustomGoal.id == pg.custom_goal_id)
                custom_goal_result = await self.db.execute(custom_goal_query)
                custom_goal = custom_goal_result.scalars().first()
                if custom_goal:
                    goal_response.custom_goal = self._custom_goal_to_response(custom_goal)
            
            response_goals.append(goal_response)
        
        return response_goals

    def _client_goal_to_response(self, goal: ClientGoal) -> ClientGoalResponse:
        """Convert a client goal model to a response schema"""
        goal_dict = {
            "id": goal.id,
            "title": goal.title,
            "description": goal.description,
            "created_at": goal.created_at,
            "updated_at": goal.updated_at
        }
        return ClientGoalResponse.model_validate(goal_dict)

    def _custom_goal_to_response(self, goal: CustomGoal) -> CustomGoalResponse:
        """Convert a custom goal model to a response schema"""
        goal_dict = {
            "id": goal.id,
            "enterprise_id": goal.enterprise_id,
            "title": goal.title,
            "description": goal.description,
            "created_at": goal.created_at,
            "updated_at": goal.updated_at
        }
        return CustomGoalResponse.model_validate(goal_dict)
