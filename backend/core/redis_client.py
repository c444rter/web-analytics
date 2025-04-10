# backend/core/redis_client.py
import os
import redis

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_db = int(os.getenv("REDIS_DB", 0))

redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
