# backend/core/redis_client.py
import os
import json
import redis
from datetime import timedelta
from urllib.parse import urlparse

# Try to use REDIS_PUBLIC_URL first, fall back to individual parameters
redis_url = os.getenv("REDIS_PUBLIC_URL")
if redis_url:
    # Parse the Redis URL to get connection details
    parsed_url = urlparse(redis_url)
    redis_host = parsed_url.hostname
    redis_port = parsed_url.port
    redis_password = parsed_url.password
    redis_user = parsed_url.username
    redis_db = int(os.getenv("REDIS_DB", 0))
    
    # Connect using URL parameters
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        username=redis_user,
        password=redis_password,
        db=redis_db,
        ssl=False  # Set to True if using SSL
    )
else:
    # Fall back to individual parameters
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_password = os.getenv("REDIS_PASSWORD")
    redis_user = os.getenv("REDIS_USER")
    redis_db = int(os.getenv("REDIS_DB", 0))
    
    # Connect using individual parameters
    if redis_password:
        redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            username=redis_user,
            password=redis_password,
            db=redis_db
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
