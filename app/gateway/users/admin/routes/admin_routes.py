'''
Temporal unprotected routes to aid development and testing.
These endpoints are designed to facilitate development and testing processes.
NOTE: These routes are intended for development purposes only and may be deprecated in the future.
'''

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from passlib.context import CryptContext

from app.gateway.database import get_db
from app.gateway.users.user.models.users import User, SubscriptionPlans
from app.gateway.users.user.schemas.user_schemas import UserCreate, UserResponse
from app.gateway.enterprises.models.enterprises import Enterprise
from app.gateway.users.admin.schemas.schema import UserCreateAdmin, UserUpdateAdmin, UserSubscriptionUpdate, UsersCreateBatch

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


admin_router = APIRouter(prefix="/admin", tags=["Admin"])

@admin_router.get(
    "/users", 
    response_model=List[UserResponse],
    summary="Get all users",
    description="Retrieves all users in the database. For development and testing only."
)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve all users from the database with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of user objects
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@admin_router.get(
    "/users/{user_id}", 
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieves a specific user by their ID. For development and testing only."
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific user by ID.
    
    Args:
        user_id: The ID of the user to retrieve
        db: Database session
        
    Returns:
        User object if found
        
    Raises:
        HTTPException: If user is not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@admin_router.post(
    "/users/create", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Creates a new user in the system. For development and testing only."
)
async def create_user(
    user_data: UserCreateAdmin,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.
    
    Args:
        user_data: User data including email, username, and password
        db: Database session
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If email or username is already in use
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user object
    hashed_password = hash_password(user_data.password)
    
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        last_name=user_data.last_name,
        first_name=user_data.first_name,
        phone_number=user_data.phone_number,
        is_active=user_data.is_active,
        is_superuser=user_data.is_superuser,
        email_verified=user_data.email_verified
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

@admin_router.post(
    "/users/create/batch", 
    response_model=List[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple users",
    description="Creates multiple users in a single request. For development and testing only."
)
async def create_users_batch(
    data: UsersCreateBatch,
    db: AsyncSession = Depends(get_db)
):
    """
    Create multiple users in a batch operation.
    
    Args:
        data: List of user data objects
        db: Database session
        
    Returns:
        List of created user objects
    """
    created_users = []
    
    for user_data in data.users:
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password,
            last_name=user_data.last_name,
            first_name=user_data.first_name,
            phone_number=user_data.phone_number,
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser,
            email_verified=user_data.email_verified
        )
        
        db.add(db_user)
        created_users.append(db_user)
    
    await db.commit()
    
    # Refresh all users to get their IDs
    for user in created_users:
        await db.refresh(user)
    
    return created_users

@admin_router.post(
    "/users/create-super", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create superuser",
    description="Creates a new superuser with administrative privileges. For development and testing only."
)
async def create_super_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new superuser with full administrative privileges.
    
    Args:
        user_data: User data including email, username, and password
        db: Database session
        
    Returns:
        Created superuser object
    """
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create superuser
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        last_name=user_data.last_name,
        first_name=user_data.first_name,
        phone_number=user_data.phone_number,
        is_active=True,
        is_superuser=True,  # Set superuser flag
        email_verified=True  # Superusers are considered verified
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

@admin_router.put(
    "/users/update/{user_id}", 
    response_model=UserResponse,
    summary="Update user",
    description="Updates a specific user's information. For development and testing only."
)
async def update_user(
    user_id: int,
    user_data: UserUpdateAdmin,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user's information.
    
    Args:
        user_id: The ID of the user to update
        user_data: Updated user data
        db: Database session
        
    Returns:
        Updated user object
        
    Raises:
        HTTPException: If user is not found
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Update user fields if provided
    update_data = user_data.model_dump(exclude_unset=True)
    
    if update_data:
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await db.commit()
    
    # Get updated user
    result = await db.execute(select(User).where(User.id == user_id))
    updated_user = result.scalars().first()
    
    return updated_user

@admin_router.delete(
    "/users/delete/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Deletes a specific user from the system. For development and testing only."
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user from the system.
    
    Args:
        user_id: The ID of the user to delete
        db: Database session
        
    Raises:
        HTTPException: If user is not found
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Delete the user
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
    
    return None

@admin_router.post(
    "/users/{user_id}/subscription", 
    response_model=UserResponse,
    summary="Update user subscription",
    description="Updates a user's subscription plan. For development and testing only."
)
async def update_user_subscription(
    user_id: int,
    subscription_data: UserSubscriptionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user's subscription plan.
    
    Args:
        user_id: The ID of the user to update
        subscription_data: New subscription plan
        db: Database session
        
    Returns:
        Updated user object
        
    Raises:
        HTTPException: If user is not found
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Update subscription
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(subscription_plan=subscription_data.subscription_plan)
    )
    await db.commit()
    
    # Get updated user
    result = await db.execute(select(User).where(User.id == user_id))
    updated_user = result.scalars().first()
    
    return updated_user


@admin_router.get("/enterprise", summary="Get all enterprises")
async def get_all_enterprises(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all enterprises.

    Args:
        db: Database session

    Returns:
        List of all enterprises
    """
    result = await db.execute(select(Enterprise).order_by(Enterprise.id))
    enterprises = result.scalars().all()
    return enterprises
