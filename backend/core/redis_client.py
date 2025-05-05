# backend/core/redis_client.py
import os
import json
import redis
from datetime import timedelta
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for REDIS_URL first (for Railway deployment)
redis_url = os.getenv("REDIS_URL")

# If REDIS_URL is available, use it directly
if redis_url:
    print(f"Using Redis URL: {redis_url}")
    redis_client = redis.from_url(redis_url)
else:
    # Fall back to individual parameters for local development
    redis_host = os.getenv("REDISHOST", "localhost")
    redis_port = int(os.getenv("REDISPORT", 6379))
    redis_password = os.getenv("REDISPASSWORD")
    redis_user = os.getenv("REDISUSER", "default")
    redis_db = int(os.getenv("REDIS_DB", 0))

    print(f"Using individual Redis parameters - Host: {redis_host}, Port: {redis_port}")

    # Connect using individual parameters
    if redis_password:
        redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            username=redis_user,
            password=redis_password,
            db=redis_db,
            ssl=False  # Set to True if using SSL
        )
    else:
        redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

# Default cache expiration time (in seconds)
DEFAULT_CACHE_EXPIRY = 60 * 60 * 6  # 1 hour

def cache_get(key):
    """
    Get a value from the cache.
    
    Args:
        key (str): The cache key
        
    Returns:
        The cached value (deserialized from JSON) or None if not found
    """
    value = redis_client.get(key)
    if value:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.decode('utf-8')
    return None

def cache_set(key, value, expiry=DEFAULT_CACHE_EXPIRY):
    """
    Set a value in the cache.
    
    Args:
        key (str): The cache key
        value: The value to cache (will be serialized to JSON)
        expiry (int): Expiration time in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        serialized = json.dumps(value)
        return redis_client.setex(key, expiry, serialized)
    except (TypeError, ValueError):
        # If value can't be JSON serialized, don't cache it
        return False

def cache_delete(key):
    """
    Delete a value from the cache.
    
    Args:
        key (str): The cache key
        
    Returns:
        int: Number of keys deleted
    """
    return redis_client.delete(key)

def cache_clear_pattern(pattern):
    """
    Delete all keys matching a pattern.
    
    Args:
        pattern (str): Pattern to match (e.g., "user:*:analytics")
        
    Returns:
        int: Number of keys deleted
    """
    keys = redis_client.keys(pattern)
    if keys:
        return redis_client.delete(*keys)
    return 0

def generate_cache_key(prefix, *args):
    """
    Generate a cache key from a prefix and arguments.
    
    Args:
        prefix (str): The prefix for the key
        *args: Additional arguments to include in the key
        
    Returns:
        str: The generated cache key
    """
    return f"{prefix}:{':'.join(str(arg) for arg in args)}"
