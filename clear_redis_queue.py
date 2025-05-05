#!/usr/bin/env python
"""
Script to clear all jobs from the Redis queue.
This will remove all queued, started, failed, and finished jobs.
"""
import os
import redis
from rq import Queue
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Redis connection parameters
redis_host = os.getenv("REDISHOST", "localhost")
redis_port = int(os.getenv("REDISPORT", 6379))
redis_password = os.getenv("REDISPASSWORD")
redis_user = os.getenv("REDISUSER", "default")

# Print connection details for debugging
print(f"Connecting to Redis at {redis_host}:{redis_port}")

# Connect to Redis
redis_conn = redis.Redis(
    host=redis_host,
    port=redis_port,
    username=redis_user,
    password=redis_password,
    ssl=False
)

# Get the default queue
queue = Queue(connection=redis_conn)

# Empty the queue
print(f"Queue stats before clearing - Queued: {len(queue.get_jobs())}")
queue.empty()
print(f"Queue stats after clearing - Queued: {len(queue.get_jobs())}")

# Also clear the failed job registry
failed_registry = queue.failed_job_registry
failed_count = len(failed_registry)
print(f"Failed jobs before clearing: {failed_count}")
for job_id in failed_registry.get_job_ids():
    failed_registry.remove(job_id)
print(f"Failed jobs after clearing: {len(failed_registry)}")

print("Redis queue has been cleared successfully!")
