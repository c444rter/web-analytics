# backend/tests/test_projections.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import app
from db.database import Base
from db import models
from core.deps import get_db, get_current_user

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

def override_get_current_user():
    return models.User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

# Fixtures
@pytest.fixture
def test_upload():
    """Create a test upload in the database."""
    db = TestingSessionLocal()
    upload = models.Upload(
        id=1,
        file_name="test_orders.csv",
        file_path="/app/uploads/test_orders.csv",
        file_size=1000,
        user_id=1,
        status="completed",
        total_rows=100,
        records_processed=100,
        uploaded_at=datetime.utcnow()
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    
    # Add some test orders
    for i in range(30):
        order_date = datetime.utcnow() - timedelta(days=i)
        order = models.Order(
            id=i+1,
            order_id=f"#{1000+i}",
            user_id=1,
            upload_id=1,
            email="customer@example.com",
            total=100.0 + i,
            subtotal=90.0 + i,
            taxes=10.0,
            created_at=order_date
        )
        db.add(order)
    
    db.commit()
    
    yield upload
    
    # Clean up
    db.query(models.Order).filter(models.Order.upload_id == 1).delete()
    db.query(models.Upload).filter(models.Upload.id == 1).delete()
    db.commit()
    db.close()

# Tests
def test_list_available_models():
    """Test the endpoint to list available forecasting models."""
    response = client.get("/projections/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "naive" in [model["id"] for model in data]
    assert "arima" in [model["id"] for model in data]

def test_get_forecast(test_upload):
    """Test the endpoint to get a forecast."""
    response = client.get(
        "/projections/forecast",
        params={"upload_id": 1, "days": 10, "model": "naive"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert "upload_id" in data
    assert data["upload_id"] == 1
    assert "days_forecasted" in data
    assert data["days_forecasted"] == 10
    assert "model" in data
    assert data["model"] == "naive"
    assert "generated_at" in data
    
    # Check forecast data
    forecast_data = data["forecast"]
    assert "forecast" in forecast_data
    assert isinstance(forecast_data["forecast"], list)
    assert len(forecast_data["forecast"]) == 10
    
    # Check first forecast item
    first_item = forecast_data["forecast"][0]
    assert "date" in first_item
    assert "predicted_revenue" in first_item
    assert "predicted_orders" in first_item
    assert "confidence" in first_item

def test_get_forecast_invalid_upload():
    """Test the endpoint with an invalid upload ID."""
    response = client.get(
        "/projections/forecast",
        params={"upload_id": 999, "days": 10, "model": "naive"}
    )
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "not found" in response.json()["detail"].lower()

def test_get_forecast_invalid_days():
    """Test the endpoint with invalid days parameter."""
    response = client.get(
        "/projections/forecast",
        params={"upload_id": 1, "days": 0, "model": "naive"}
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "days" in response.json()["detail"].lower()
    
    response = client.get(
        "/projections/forecast",
        params={"upload_id": 1, "days": 366, "model": "naive"}
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "days" in response.json()["detail"].lower()

def test_get_forecast_invalid_model():
    """Test the endpoint with an invalid model."""
    response = client.get(
        "/projections/forecast",
        params={"upload_id": 1, "days": 10, "model": "invalid_model"}
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "model" in response.json()["detail"].lower()
