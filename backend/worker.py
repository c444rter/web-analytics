# backend/worker.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rq import Worker, Queue
from redis import Redis
from core.redis_client import redis_client

# Set environment variable to fix fork() issue on macOS
# NOTE: This environment variable should ideally be set BEFORE Python starts
# For local development, use: OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES python worker.py
# or use the start_worker.sh script which sets this environment variable
# For production, this is set in Dockerfile, docker-compose.yml, and railway.toml
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Print environment variables for debugging
print(f"SUPABASE_URL: {os.environ.get('SUPABASE_URL')}")
print(f"BUCKET_NAME: {os.environ.get('BUCKET_NAME')}")

listen = ['default']

if __name__ == '__main__':
    worker = Worker(list(map(lambda queue_name: Queue(queue_name, connection=redis_client), listen)))
    worker.work()
