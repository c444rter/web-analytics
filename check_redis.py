import os
import redis
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Redis configuration from environment variables
REDIS_PUBLIC_URL = os.environ.get("REDIS_PUBLIC_URL")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_USER = os.environ.get("REDIS_USER")
REDIS_DB = os.environ.get("REDIS_DB", "0")

print(f"REDIS_PUBLIC_URL: {REDIS_PUBLIC_URL}")
print(f"REDIS_HOST: {REDIS_HOST}")
print(f"REDIS_PORT: {REDIS_PORT}")
print(f"REDIS_PASSWORD: {'*' * len(REDIS_PASSWORD) if REDIS_PASSWORD else None}")
print(f"REDIS_USER: {REDIS_USER}")
print(f"REDIS_DB: {REDIS_DB}")

# Try to connect using REDIS_PUBLIC_URL
if REDIS_PUBLIC_URL:
    print("\nTrying to connect using REDIS_PUBLIC_URL...")
    try:
        # Parse the Redis URL to get connection details
        parsed_url = urlparse(REDIS_PUBLIC_URL)
        redis_host = parsed_url.hostname
        redis_port = parsed_url.port
        redis_password = parsed_url.password
        redis_user = parsed_url.username
        redis_db = int(REDIS_DB)
        
        print(f"  Parsed host: {redis_host}")
        print(f"  Parsed port: {redis_port}")
        print(f"  Parsed user: {redis_user}")
        print(f"  Parsed password: {'*' * len(redis_password) if redis_password else None}")
        
        # Connect using URL parameters
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            username=redis_user,
            password=redis_password,
            db=redis_db,
            socket_timeout=5,
            socket_connect_timeout=5
        )
        
        # Test the connection
        ping_result = redis_client.ping()
        print(f"  Connection successful! Ping result: {ping_result}")
        
        # Set and get a test value
        redis_client.set("test_key", "test_value")
        test_value = redis_client.get("test_key")
        print(f"  Test value: {test_value.decode('utf-8') if test_value else None}")
        
        # Clean up
        redis_client.delete("test_key")
        
    except Exception as e:
        print(f"  Connection failed: {str(e)}")

# Try to connect using individual parameters
if REDIS_HOST and REDIS_PORT:
    print("\nTrying to connect using individual parameters...")
    try:
        # Connect using individual parameters
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=int(REDIS_PORT),
            username=REDIS_USER,
            password=REDIS_PASSWORD,
            db=int(REDIS_DB),
            socket_timeout=5,
            socket_connect_timeout=5
        )
        
        # Test the connection
        ping_result = redis_client.ping()
        print(f"  Connection successful! Ping result: {ping_result}")
        
        # Set and get a test value
        redis_client.set("test_key", "test_value")
        test_value = redis_client.get("test_key")
        print(f"  Test value: {test_value.decode('utf-8') if test_value else None}")
        
        # Clean up
        redis_client.delete("test_key")
        
    except Exception as e:
        print(f"  Connection failed: {str(e)}")
