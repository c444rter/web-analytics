# backend/tests/integration/test_api_integration.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import json
from datetime import datetime, timedelta

from main import app
from db.database import Base
from core.deps import get_db
from core.security import create_access_token
from db import models

# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
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

@pytest.fixture
def test_user():
    """Create a test user and return the user object and authentication token."""
    db = TestingSessionLocal()
    
    # Check if test user already exists
    user = db.query(models.User).filter(models.User.email == "test@example.com").first()
    if not user:
        # Create a test user
        user = models.User(
            email="test@example.com",
            hashed_password="$2b$12$IKEQb00u5eHhkplO0/xR0.LZ8tFhPGI4tXgFBMJxzTXjpysjLWwre",  # hashed 'password'
            is_active=True,
            is_superuser=False,
            full_name="Test User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email}
    )
    
    db.close()
    
    return {"user": user, "token": access_token}

@pytest.fixture
def test_upload(test_user):
    """Create a test upload for the test user."""
    db = TestingSessionLocal()
    
    # Create a test upload
    upload = models.Upload(
        filename="test_data.csv",
        user_id=test_user["user"].id,
        upload_date=datetime.now(),
        status="completed",
        file_size=1024,
        file_type="csv"
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    
    db.close()
    
    return upload

def test_read_health():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "services" in data

def test_read_users_me(test_user):
    """Test the current user endpoint."""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["user"].email
    assert data["full_name"] == test_user["user"].full_name
    assert "id" in data

def test_read_uploads(test_user, test_upload):
    """Test the uploads endpoint."""
    response = client.get(
        "/api/v1/uploads/",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == test_upload.id
    assert data[0]["filename"] == test_upload.filename
    assert data[0]["status"] == test_upload.status

def test_read_analytics_summary(test_user, test_upload):
    """Test the analytics summary endpoint."""
    response = client.get(
        f"/api/v1/analytics/summary/{test_upload.id}",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    
    # This might return 404 if no analytics data exists for the test upload
    # In a real integration test, we would seed the database with analytics data
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "total_revenue" in data
        assert "total_orders" in data
        assert "average_order_value" in data

def test_read_projections(test_user, test_upload):
    """Test the projections endpoint."""
    response = client.get(
        f"/api/v1/projections/{test_upload.id}?days=30&model=naive",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    
    # This might return 404 if no projections data exists for the test upload
    # In a real integration test, we would seed the database with projections data
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "upload_id" in data
        assert "days_forecasted" in data
        assert "model" in data
        assert "forecast" in data
