# backend/api/v1/projections.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from core.deps import get_db, get_current_user
from db import models
from ml import TimeSeriesForecaster, StyleForecaster
from core.redis_client import cache_get, cache_set, generate_cache_key

router = APIRouter(tags=["projections"])

@router.get("/forecast")
def get_sales_forecast(
    upload_id: int,
    days: Optional[int] = Query(30, description="Number of days to forecast"),
    model: Optional[str] = Query("naive", description="Forecasting model to use (naive, arima)"),
    refresh_cache: Optional[bool] = Query(False, description="Force refresh the cache"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Generate a sales forecast for the specified upload.
    
    Args:
        upload_id: The ID of the uploaded orders file
        days: Number of days to forecast (default: 30)
        model: Forecasting model to use (default: naive)
        refresh_cache: Whether to force refresh the cache
        
    Returns:
        Dictionary with forecast results
    """
    # Validate parameters
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
    
    if model not in ["naive", "arima"]:
        raise HTTPException(status_code=400, detail="Model must be 'naive' or 'arima'")
    
    # Check if the upload exists and belongs to the user
    upload = db.query(models.Upload).filter(
        models.Upload.id == upload_id,
        models.Upload.user_id == current_user.id
    ).first()
    
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Generate cache key
    cache_key = generate_cache_key(
        "projections:forecast", 
        current_user.id, 
        upload_id, 
        days, 
        model
    )
    
    # Check cache if refresh_cache is False
    if not refresh_cache:
        cached_data = cache_get(cache_key)
        if cached_data:
            return cached_data
    
    # Create forecaster and generate forecast
    forecaster = TimeSeriesForecaster(db, current_user.id, upload_id)
    forecast_data = forecaster.forecast(days=days, model=model)
    
    # Add metadata
    result = {
        "upload_id": upload_id,
        "days_forecasted": days,
        "model": model,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "forecast": forecast_data
    }
    
    # Cache the result
    cache_set(cache_key, result)
    
    return result

@router.get("/style-forecast")
def get_style_forecast(
    upload_id: int,
    days: Optional[int] = Query(30, description="Number of days to forecast"),
    model: Optional[str] = Query("naive", description="Forecasting model to use (naive, arima)"),
    refresh_cache: Optional[bool] = Query(False, description="Force refresh the cache"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Generate a forecast for product styles for the specified upload.
    
    Args:
        upload_id: The ID of the uploaded orders file
        days: Number of days to forecast (default: 30)
        model: Forecasting model to use (default: naive)
        refresh_cache: Whether to force refresh the cache
        
    Returns:
        Dictionary with style forecast results
    """
    # Validate parameters
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
    
    if model not in ["naive", "arima"]:
        raise HTTPException(status_code=400, detail="Model must be 'naive' or 'arima'")
    
    # Check if the upload exists and belongs to the user
    upload = db.query(models.Upload).filter(
        models.Upload.id == upload_id,
        models.Upload.user_id == current_user.id
    ).first()
    
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Generate cache key
    cache_key = generate_cache_key(
        "projections:style-forecast", 
        current_user.id, 
        upload_id, 
        days, 
        model
    )
    
    # Check cache if refresh_cache is False
    if not refresh_cache:
        cached_data = cache_get(cache_key)
        if cached_data:
            return cached_data
    
    # Create style forecaster and generate forecast
    forecaster = StyleForecaster(db, current_user.id, upload_id)
    forecast_data = forecaster.forecast(days=days, model=model)
    
    # Add metadata
    result = {
        "upload_id": upload_id,
        "days_forecasted": days,
        "model": model,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "forecast": forecast_data
    }
    
    # Cache the result
    cache_set(cache_key, result)
    
    return result

@router.get("/models")
def list_available_models():
    """
    List available forecasting models.
    
    Returns:
        List of available models with descriptions
    """
    models = [
        {
            "id": "naive",
            "name": "Naive Seasonal",
            "description": "Simple forecasting based on historical averages by day of week",
            "recommended_for": "Quick forecasts with limited historical data"
        },
        {
            "id": "arima",
            "name": "ARIMA",
            "description": "Auto-Regressive Integrated Moving Average model",
            "recommended_for": "More accurate forecasts with sufficient historical data"
        }
    ]
    
    return models
