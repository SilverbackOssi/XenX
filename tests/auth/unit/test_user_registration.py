import pytest 
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
# from app.models.user import UserRole
from app.auth.database import Base, engine
import asyncio

# Test data
valid_user_data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test@123",  # Meets password requirements
    "role": "cpa",
    "last_name": "User",
    "first_name": "Test",
    "phone_number": "1234567890"
}

@pytest_asyncio.fixture(scope="function")
async def async_client():
    from main import app  # Import here to avoid db conflicts
    
    # Create clean database for each test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_valid_user_registration(async_client: AsyncClient):
    response = await async_client.post("/auth/register", json=valid_user_data) # type: ignore
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == valid_user_data["email"]
    assert data["username"] == valid_user_data["username"]
    assert data["role"] == valid_user_data["role"]
    assert "password" not in data

@pytest.mark.asyncio
async def test_duplicate_email_registration(async_client: AsyncClient):
    # Register first user
    response = await async_client.post("/auth/register", json=valid_user_data) # type: ignore
    assert response.status_code == 201

    # Try to register with same email
    response = await async_client.post(
        "/auth/register",
        json={**valid_user_data, "username": "different"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_invalid_email_format(async_client: AsyncClient):
    invalid_data = {**valid_user_data, "email": "invalid-email"}
    response = await async_client.post("/auth/register", json=invalid_data)  # type: ignore
    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.asyncio
async def test_weak_password(async_client: AsyncClient):
    invalid_data = {**valid_user_data, "password": "weak"}
    response = await async_client.post("/auth/register", json=invalid_data)  # type: ignore
    assert response.status_code == 400
    assert "Password must" in response.json()["detail"]

@pytest.mark.asyncio
async def test_missing_required_fields(async_client: AsyncClient):
    invalid_data = {
        "email": "test@example.com",
        # Missing username and password
        "role": "cpa"
    }
    response = await async_client.post("/auth/register", json=invalid_data)  # type: ignore
    assert response.status_code == 422  # Pydantic validation error
