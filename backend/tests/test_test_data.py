# backend/tests/test_test_data.py

import pytest
import os
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

# Tests
def test_generate_test_data():
    """Test the endpoint to generate test data."""
    # Create a temporary directory for test uploads
    os.makedirs("/tmp/uploads", exist_ok=True)
    
    # Mock the UPLOAD_DIR in the test_data module
    import backend.api.v1.test_data as test_data_module
    original_upload_dir = test_data_module.UPLOAD_DIR
    test_data_module.UPLOAD_DIR = "/tmp/uploads"
    
    try:
        # Test data request
        request_data = {
            "num_orders": 10,
            "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "min_items_per_order": 1,
            "max_items_per_order": 3,
            "include_discounts": True,
            "include_shipping": True,
            "include_taxes": True,
            "output_file": "test_generated_data.csv"
        }
        
        response = client.post("/test-data/generate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "file_path" in data
        assert "num_orders" in data
        assert "num_line_items" in data
        assert "date_range" in data
        
        # Check values
        assert data["num_orders"] == 10
        assert data["num_line_items"] > 0
        
        # Check that the file was created
        output_path = os.path.join("/tmp/uploads", "test_generated_data.csv")
        assert os.path.exists(output_path)
        
        # Check file content
        with open(output_path, "r") as f:
            content = f.read()
            assert "Name,Email,Financial Status" in content
            assert "Lineitem quantity,Lineitem name" in content
    
    finally:
        # Restore the original UPLOAD_DIR
        test_data_module.UPLOAD_DIR = original_upload_dir
        
        # Clean up
        output_path = os.path.join("/tmp/uploads", "test_generated_data.csv")
        if os.path.exists(output_path):
            os.remove(output_path)

def test_generate_test_data_validation():
    """Test validation for the test data generation endpoint."""
    # Test with invalid num_orders
    request_data = {
        "num_orders": 0,  # Invalid: must be >= 1
        "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
        "end_date": datetime.utcnow().isoformat(),
    }
    
    response = client.post("/test-data/generate", json=request_data)
    assert response.status_code == 422  # Validation error
    
    # Test with invalid date range
    request_data = {
        "num_orders": 10,
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),  # End date before start date
    }
    
    response = client.post("/test-data/generate", json=request_data)
    assert response.status_code == 500  # Server error due to invalid date range
    assert "Error generating test data" in response.json()["detail"]
    
    # Test with missing required fields
    request_data = {
        "num_orders": 10,
        # Missing start_date and end_date
    }
    
    response = client.post("/test-data/generate", json=request_data)
    assert response.status_code == 422  # Validation error
