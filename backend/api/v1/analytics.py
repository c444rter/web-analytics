# api/v1/analytics.py

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from core.deps import get_db, get_current_user
from analytics_service import ANALYTICS_REGISTRY
from core.redis_client import cache_get, cache_set, generate_cache_key, cache_clear_pattern


router = APIRouter()

@router.get("/available")
def list_available_analytics():
    """
    Returns a list of all possible analytics the user can request.
    Each item has { "key", "label", "description" }.
    """
    # This rarely changes, so we can cache it
    cache_key = "analytics:available"
    cached_data = cache_get(cache_key)
    if cached_data:
        return cached_data
    
    all_metrics = []
    for key, info in ANALYTICS_REGISTRY.items():
        all_metrics.append({
            "key": key,
            "label": info["label"],
            "description": info["description"]
        })
    
    # Cache the result
    cache_set(cache_key, all_metrics)
    return all_metrics

@router.get("/full")
def analytics_full(
    upload_id: int,
    refresh_cache: Optional[bool] = Query(False, description="Force refresh the cache"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Returns ALL analytics from the registry in one shot.
    """
    # Generate a cache key based on the user and upload
    cache_key = generate_cache_key("analytics:full", current_user.id, upload_id)
    
    # Check if we have cached data and refresh_cache is not True
    if not refresh_cache:
        cached_data = cache_get(cache_key)
        if cached_data:
            return cached_data
    
    # We'll iterate over every key in the registry
    result = {}
    for key, info in ANALYTICS_REGISTRY.items():
        handler_func = info["handler"]
        if not handler_func:
            # If there's no function for some reason, skip or set an empty value
            result[key] = None
            continue
        # Call the aggregator function
        result[key] = handler_func(db, current_user.id, upload_id)
    
    # Cache the result
    cache_set(cache_key, result)
    return result

@router.post("/custom")
def analytics_custom(
    upload_id: int,
    selected_metrics: List[str] = Body(...),
    refresh_cache: Optional[bool] = Query(False, description="Force refresh the cache"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Lets the frontend specify which KPI(s) to fetch by passing a list of keys.
    Example JSON body:
      ["orders_summary", "time_series", "top_cities_by_orders"]
    """
    # Generate a cache key based on the user, upload, and selected metrics
    metrics_key = "-".join(sorted(selected_metrics))  # Sort to ensure consistent key
    cache_key = generate_cache_key("analytics:custom", current_user.id, upload_id, metrics_key)
    
    # Check if we have cached data and refresh_cache is not True
    if not refresh_cache:
        cached_data = cache_get(cache_key)
        if cached_data:
            return cached_data
    
    response_data = {}
    for metric_key in selected_metrics:
        info = ANALYTICS_REGISTRY.get(metric_key)
        if not info:
            # If user gave an unknown key, decide how to handle:
            response_data[metric_key] = {"error": "Unknown KPI key"}
            continue

        handler_func = info["handler"]
        if handler_func is None:
            response_data[metric_key] = {"error": "No handler function available"}
            continue

        # Call aggregator
        response_data[metric_key] = handler_func(db, current_user.id, upload_id)

    # Cache the result
    cache_set(cache_key, response_data)
    return response_data

@router.post("/clear-cache")
def clear_analytics_cache(
    upload_id: Optional[int] = Query(None, description="Clear cache for specific upload, or all if not provided"),
    current_user=Depends(get_current_user)
):
    """
    Clears the analytics cache for the current user.
    If upload_id is provided, only clears cache for that upload.
    """
    if upload_id:
        pattern = f"analytics:*:{current_user.id}:{upload_id}:*"
        cache_clear_pattern(pattern)
        return {"message": f"Cache cleared for upload {upload_id}"}
    else:
        pattern = f"analytics:*:{current_user.id}:*"
        cache_clear_pattern(pattern)
        return {"message": "All analytics cache cleared for current user"}
