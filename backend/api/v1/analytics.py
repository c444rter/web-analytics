# api/v1/analytics.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from sqlalchemy.orm import Session

from core.deps import get_db, get_current_user
from analytics_service import ANALYTICS_REGISTRY  # <-- Make sure you import the registry!


router = APIRouter()

@router.get("/available")
def list_available_analytics():
    """
    Returns a list of all possible analytics the user can request.
    Each item has { "key", "label", "description" }.
    """
    all_metrics = []
    for key, info in ANALYTICS_REGISTRY.items():
        all_metrics.append({
            "key": key,
            "label": info["label"],
            "description": info["description"]
        })
    return all_metrics

@router.get("/full")
def analytics_full(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Returns ALL analytics from the registry in one shot.
    """
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
    return result

@router.post("/custom")
def analytics_custom(
    upload_id: int,
    selected_metrics: List[str] = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Lets the frontend specify which KPI(s) to fetch by passing a list of keys.
    Example JSON body:
      ["orders_summary", "time_series", "top_cities_by_orders"]
    """
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

    return response_data