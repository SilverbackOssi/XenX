import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.auth.models.user import User, Role, Permission
from app.auth.services.auth_service import AuthService
from app.core.config import settings

def test_register_valid_user(client: TestClient, db: Session):
    """Test registering a new user with valid data."""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test123!@#",
            "organization_name": "Test Org"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data
    
    # Verify user in database
    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.is_active
    assert not user.is_verified
    assert not user.mfa_enabled

def test_register_duplicate_email(client: TestClient, db: Session):
    """Test registering with an email that already exists."""
    # Create initial user
    client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "username": "firstuser",
            "password": "Test123!@#"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "username": "seconduser",
            "password": "Test123!@#"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success(client: TestClient, test_user: User):
    """Test successful login with correct credentials."""
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": "testpass123",
            "scope": ""
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_with_mfa(client: TestClient, test_user_with_mfa: User):
    """Test login with MFA enabled."""
    # First try without MFA code
    response = client.post(
        "/auth/login",
        data={
            "username": test_user_with_mfa.email,
            "password": "testpass123",
            "scope": ""
        }
    )
    
    assert response.status_code == 401
    assert "MFA code required" in response.json()["detail"]
    
    # Try with invalid MFA code
    response = client.post(
        "/auth/login",
        data={
            "username": test_user_with_mfa.email,
            "password": "testpass123",
            "scope": "123456"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid MFA code" in response.json()["detail"]

def test_login_rate_limiting(client: TestClient, test_user: User):
    """Test account lockout after multiple failed attempts."""
    # Make multiple failed login attempts
    for _ in range(settings.MAX_LOGIN_ATTEMPTS):
        response = client.post(
            "/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpass",
                "scope": ""
            }
        )
        assert response.status_code == 401
    
    # Try one more time - should be locked
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpass",
            "scope": ""
        }
    )
    
    assert response.status_code == 403
    assert "Account locked" in response.json()["detail"]

def test_refresh_token(client: TestClient, test_user: User, auth_service: AuthService):
    """Test refresh token functionality."""
    # First login to get tokens
    tokens = auth_service.create_tokens(test_user)
    
    # Use refresh token to get new access token
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens.refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] != tokens.access_token

def test_logout(client: TestClient, test_user: User, auth_service: AuthService):
    """Test logout functionality."""
    # First login to get tokens
    tokens = auth_service.create_tokens(test_user)
    
    # Logout
    response = client.post(
        "/auth/logout",
        json={"refresh_token": tokens.refresh_token},
        headers={"Authorization": f"Bearer {tokens.access_token}"}
    )
    
    assert response.status_code == 200
    
    # Try to use refresh token after logout
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens.refresh_token}
    )
    
    assert response.status_code == 401

@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    auth_service = AuthService(db)
    user = auth_service.create_user(
        UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
    )
    return user

@pytest.fixture
def test_user_with_mfa(db: Session):
    """Create a test user with MFA enabled."""
    auth_service = AuthService(db)
    user = auth_service.create_user(
        UserCreate(
            email="mfa@example.com",
            username="mfauser",
            password="testpass123"
        )
    )
    auth_service.setup_mfa(user)
    return user
