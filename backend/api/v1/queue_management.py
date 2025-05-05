from fastapi import APIRouter, Depends, HTTPException, status
import redis
from rq import Queue
import os
from typing import Dict
from core.deps import get_current_user
from db import models

# Create a router
router = APIRouter()

def get_redis_connection():
    """Get Redis connection using environment variables"""
    # Check for REDIS_URL first (for Railway deployment)
    redis_url = os.getenv("REDIS_URL")
    
    # If REDIS_URL is available, use it directly
    if redis_url:
        print(f"Queue management using Redis URL: {redis_url}")
        return redis.from_url(redis_url)
    else:
        # Fall back to individual parameters for local development
        redis_host = os.getenv("REDISHOST", "localhost")
        redis_port = int(os.getenv("REDISPORT", 6379))
        redis_password = os.getenv("REDISPASSWORD")
        redis_user = os.getenv("REDISUSER", "default")
        
        print(f"Queue management using individual Redis parameters - Host: {redis_host}, Port: {redis_port}")
        
        return redis.Redis(
            host=redis_host,
            port=redis_port,
            username=redis_user,
            password=redis_password,
            ssl=False
        )

@router.post("/clear", status_code=status.HTTP_200_OK)
async def clear_queue(current_user: models.User = Depends(get_current_user)) -> Dict:
    """
    Clear all jobs from the Redis queue.
    Requires admin authentication.
    """
    # Check if the user is an admin (assuming user with ID 1 is admin)
    if current_user.id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    try:
        # Connect to Redis
        redis_conn = get_redis_connection()
        
        # Get the default queue
        queue = Queue(connection=redis_conn)
        
        # Get stats before clearing
        queued_before = len(queue.get_jobs())
        failed_registry = queue.failed_job_registry
        failed_before = len(failed_registry)
        
        # Empty the queue
        queue.empty()
        
        # Clear failed jobs
        for job_id in failed_registry.get_job_ids():
            failed_registry.remove(job_id)
        
        return {
            "status": "success",
            "message": "Redis queue cleared successfully",
            "stats": {
                "queued_before": queued_before,
                "queued_after": len(queue.get_jobs()),
                "failed_before": failed_before,
                "failed_after": len(failed_registry)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear Redis queue: {str(e)}"
        )

@router.get("/status", status_code=status.HTTP_200_OK)
async def queue_status() -> Dict:
    """
    Get the current status of the Redis queue.
    """
    try:
        # Connect to Redis
        redis_conn = get_redis_connection()
        
        # Get the default queue
        queue = Queue(connection=redis_conn)
        
        # Get queue stats
        failed_registry = queue.failed_job_registry
        finished_registry = queue.finished_job_registry
        started_registry = queue.started_job_registry
        
        return {
            "status": "success",
            "queue_stats": {
                "queued": len(queue.get_jobs()),
                "started": len(started_registry),
                "failed": len(failed_registry),
                "finished": len(finished_registry)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Redis queue status: {str(e)}"
        )
