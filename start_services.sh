#!/bin/bash

# Kill any existing processes
pkill -f "uvicorn main:app" || true
pkill -f "python worker.py" || true

# Set environment variable to fix fork() issue on macOS
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Start the backend server
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
echo "Backend server started on http://localhost:8000"

# Wait a moment for the server to start
sleep 2

# Start the worker with the environment variable set
./start_worker.sh &
echo "Worker started with OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES"

echo "All services started. Press Ctrl+C to stop all services."

# Wait for user to press Ctrl+C
wait
