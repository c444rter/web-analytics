# api/v1/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import json
import datetime
import math
from typing import Optional
from db import models, schemas
from core.deps import get_current_user, get_db

router = APIRouter(tags=["dashboard"])

@router.get("/orders-summary", summary="Orders Summary Dashboard")
def orders_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    upload_id: Optional[int] = Query(None, description="The ID of the uploaded orders file")
):
    # Ensure an upload_id is provided
    if not upload_id:
        raise HTTPException(
            status_code=400, detail="Missing upload identifier. Please select an upload."
        )
    
    # Build query filtered by current user and the provided upload_id
    query = db.query(models.Order).filter(
        models.Order.user_id == current_user.id,
        models.Order.upload_id == upload_id
    )
    
    orders = query.all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for the selected upload.")
    
    # Aggregate metrics: total orders and total revenue.
    total_orders = len(orders)
    total_revenue = 0.0
    for o in orders:
        try:
            val = float(o.total) if o.total and o.total.strip() != "" else 0.0
            if not math.isfinite(val):
                val = 0.0
        except Exception:
            val = 0.0
        total_revenue += val

    summary = {
        "upload_id": upload_id,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    
    return summary
