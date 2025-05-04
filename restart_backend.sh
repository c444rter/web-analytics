#!/bin/bash

# Kill the existing backend process
pkill -f "uvicorn main:app"

# Start the backend server
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &

echo "Backend server restarted"
