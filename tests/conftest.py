# testing configuration and fixtures file

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from redis import Redis
from fakeredis import FakeRedis

from app.main import app
from app.database import Base, get_db
from app.core.dependencies import get_redis

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    # Create the database and tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def redis():
    redis = FakeRedis()
    return redis

@pytest.fixture(scope="function")
def client(db, redis):
    def override_get_db():
        try:
            yield db
        finally:
            db.rollback()
    
    def override_get_redis():
        return redis
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()
