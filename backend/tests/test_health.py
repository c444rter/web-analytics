# backend/tests/test_health.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from main import app
from db.database import Base, get_db

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test tables
Base.metadata.create_all(bind=engine)

# Override the dependencies
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health_check_success():
    """Test the health check endpoint when all services are healthy."""
    # Mock Redis ping to return True
    with patch('main.redis_client') as mock_redis:
        mock_redis.ping.return_value = True
        
        # Call the health check endpoint
        response = client.get("/health")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["services"]["database"] == "connected"
        assert data["services"]["redis"] == "connected"

def test_health_check_database_failure():
    """Test the health check endpoint when the database is unhealthy."""
    # Mock the database session to raise an exception
    with patch('main.get_db') as mock_get_db:
        # Create a mock session that raises an exception when execute is called
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception("Database connection error")
        
        # Configure the mock to yield our mock session
        mock_get_db.return_value = mock_session
        
        # Mock Redis ping to return True
        with patch('main.redis_client') as mock_redis:
            mock_redis.ping.return_value = True
            
            # Override the app's dependency
            app.dependency_overrides[get_db] = lambda: mock_session
            
            # Call the health check endpoint
            response = client.get("/health")
            
            # Check the response
            assert response.status_code == 503
            data = response.json()
            assert data["detail"]["status"] == "unhealthy"
            assert "timestamp" in data["detail"]
            assert "error" in data["detail"]["services"]["database"]
            assert data["detail"]["services"]["redis"] == "connected"
            
            # Restore the original dependency override
            app.dependency_overrides[get_db] = override_get_db

def test_health_check_redis_failure():
    """Test the health check endpoint when Redis is unhealthy."""
    # Mock Redis ping to raise an exception
    with patch('main.redis_client') as mock_redis:
        mock_redis.ping.side_effect = Exception("Redis connection error")
        
        # Call the health check endpoint
        response = client.get("/health")
        
        # Check the response
        assert response.status_code == 503
        data = response.json()
        assert data["detail"]["status"] == "unhealthy"
        assert "timestamp" in data["detail"]
        assert data["detail"]["services"]["database"] == "connected"
        assert "error" in data["detail"]["services"]["redis"]

def test_health_check_all_services_failure():
    """Test the health check endpoint when all services are unhealthy."""
    # Mock the database session to raise an exception
    with patch('main.get_db') as mock_get_db:
        # Create a mock session that raises an exception when execute is called
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception("Database connection error")
        
        # Configure the mock to yield our mock session
        mock_get_db.return_value = mock_session
        
        # Mock Redis ping to raise an exception
        with patch('main.redis_client') as mock_redis:
            mock_redis.ping.side_effect = Exception("Redis connection error")
            
            # Override the app's dependency
            app.dependency_overrides[get_db] = lambda: mock_session
            
            # Call the health check endpoint
            response = client.get("/health")
            
            # Check the response
            assert response.status_code == 503
            data = response.json()
            assert data["detail"]["status"] == "unhealthy"
            assert "timestamp" in data["detail"]
            assert "error" in data["detail"]["services"]["database"]
            assert "error" in data["detail"]["services"]["redis"]
            
            # Restore the original dependency override
            app.dependency_overrides[get_db] = override_get_db
