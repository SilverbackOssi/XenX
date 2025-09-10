

# Tax Plan routes
from fastapi import APIRouter


tax_plan_router = APIRouter(
    prefix="/tax-plans",
    tags=["Tax Plans"],
    responses={404: {"description": "Not found"}},
)

# POST, generate tax plan; generate tax plan with AI
# POST, prepare slide; prepare presentation slides from task plan
# POST, create proposal; generate a proposal from the tax plan
# GET, get tax plans by project
# GET, get tax plan details by id