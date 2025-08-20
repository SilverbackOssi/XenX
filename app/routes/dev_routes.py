'''
Temporal routes to aid development and testing
'''

from typing import List
from fastapi import APIRouter

from app.auth.models.users import User


dev_router = APIRouter(prefix="/dev", tags=["temp"])
'''
GET /dev/users/all
GET /dev/users/{user_id}
POST /dev/users/create
PUT /dev/users/update/{user_id}
DELETE /dev/users/delete/{user_id}
'''

@dev_router.get("/users/all", response_model=List[User])
async def get_all_users():
    pass

@dev_router.get("/users/{user_id}")
async def get_user(user_id: int):
    pass

@dev_router.post("/users/create")
async def create_user():
    pass

@dev_router.post("/users/create/batch")
async def create_users_batch():
    pass

@dev_router.post("/users/create-super")
async def create_super_user():
    # create a user, then set is_superuser to True
    pass

@dev_router.put("/users/update/{user_id}")
async def update_user(user_id: int):
    pass

@dev_router.delete("/users/delete/{user_id}")
async def delete_user(user_id: int):
    pass

@dev_router.post("/users/{user_id}/subscription")
async def update_user_subscription(user_id: int):
    pass
