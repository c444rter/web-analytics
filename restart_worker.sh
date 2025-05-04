#!/bin/bash

# Kill any existing worker processes
pkill -f "python worker.py"

# Set environment variable to fix fork() issue on macOS
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Start the worker with the environment variable set
./start_worker.sh &

echo "Worker restarted with OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES"
