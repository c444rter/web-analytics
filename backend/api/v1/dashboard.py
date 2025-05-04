# api/v1/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import json
import datetime
import math
from typing import Optional, Dict, Any, List
from db import models, schemas
from core.deps import get_current_user, get_db
from core.redis_client import cache_get, cache_set, generate_cache_key, redis_client
from rq import Queue
from rq.registry import StartedJobRegistry, FinishedJobRegistry
from rq.queue import FailedQueue

router = APIRouter(tags=["dashboard"])

@router.get("/orders-summary", summary="Orders Summary Dashboard")
def orders_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    upload_id: Optional[int] = Query(None, description="The ID of the uploaded orders file"),
    refresh_cache: Optional[bool] = Query(False, description="Force refresh the cache")
):
    # Ensure an upload_id is provided
    if not upload_id:
        raise HTTPException(
            status_code=400, detail="Missing upload identifier. Please select an upload."
        )
    
    # Generate a cache key based on the user and upload
    cache_key = generate_cache_key("dashboard:orders_summary", current_user.id, upload_id)
    
    # Check if we have cached data and refresh_cache is not True
    if not refresh_cache:
        cached_data = cache_get(cache_key)
        if cached_data:
            return cached_data
    
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
        # Since total is now stored as Numeric in the database, we can use it directly
        if o.total is not None:
            try:
                # Convert Decimal to float for JSON serialization
                val = float(o.total)
                if math.isfinite(val):  # Check if the value is finite
                    total_revenue += val
            except (ValueError, TypeError):
                # Skip invalid values
                pass

    # Calculate average order value
    avg_order_value = 0.0
    if total_orders > 0:
        avg_order_value = total_revenue / total_orders

    summary = {
        "upload_id": upload_id,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "average_order_value": avg_order_value,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    
    # Cache the result
    cache_set(cache_key, summary)
    
    return summary

@router.get("/redis-status", response_model=Dict[str, Any])
def get_redis_status(current_user: models.User = Depends(get_current_user)):
    """Get Redis queue status information."""
    try:
        # Check Redis connection
        redis_connected = redis_client.ping()
        
        # Get queue information
        queue = Queue(connection=redis_client)
        registry = StartedJobRegistry(queue=queue)
        
        # Get counts
        queued_jobs = queue.count
        started_jobs = len(registry.get_job_ids())
        
        # Get job IDs
        queued_job_ids = queue.job_ids
        started_job_ids = registry.get_job_ids()
        
        # Get failed jobs
        failed_queue = FailedQueue(connection=redis_client)
        failed_job_ids = failed_queue.job_ids
        failed_jobs = len(failed_job_ids)
        
        # Get completed jobs (last 100)
        finished_registry = FinishedJobRegistry(queue=queue)
        finished_job_ids = finished_registry.get_job_ids()
        finished_jobs = len(finished_job_ids)
        
        # Get job details
        job_details = []
        for job_id in queued_job_ids + started_job_ids + failed_job_ids + finished_job_ids[:20]:
            job = queue.fetch_job(job_id)
            if job:
                job_details.append({
                    "id": job.id,
                    "status": job.get_status(),
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "enqueued_at": job.enqueued_at.isoformat() if job.enqueued_at else None,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "ended_at": job.ended_at.isoformat() if job.ended_at else None,
                    "exc_info": job.exc_info if hasattr(job, 'exc_info') else None,
                    "meta": job.meta
                })
        
        return {
            "redis_connected": redis_connected,
            "queue_stats": {
                "queued": queued_jobs,
                "started": started_jobs,
                "failed": failed_jobs,
                "finished": finished_jobs
            },
            "job_details": job_details
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting Redis status: {str(e)}"
        )
