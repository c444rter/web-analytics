#!/usr/bin/env python
"""
API endpoint to clear all jobs from the Redis queue.
This can be added to your FastAPI app to allow clearing the queue via an API call.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
from rq import Queue
import os
from typing import Dict

# Create a router
router = APIRouter()

# Security scheme
security = HTTPBearer()

# Admin token for authentication
ADMIN_TOKEN = os.getenv("SECRET_KEY", "default-secret-key")

def get_redis_connection():
    """Get Redis connection using environment variables"""
    redis_host = os.getenv("REDISHOST", "localhost")
    redis_port = int(os.getenv("REDISPORT", 6379))
    redis_password = os.getenv("REDISPASSWORD")
    redis_user = os.getenv("REDISUSER", "default")
    
    return redis.Redis(
        host=redis_host,
        port=redis_port,
        username=redis_user,
        password=redis_password,
        ssl=False
    )

@router.post("/api/admin/clear-queue", status_code=status.HTTP_200_OK)
async def clear_queue(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, str]:
    """
    Clear all jobs from the Redis queue.
    Requires admin token for authentication.
    """
    # Verify token
    if credentials.credentials != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
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

# To use this in your FastAPI app, add the router to your app:
# app.include_router(router)
