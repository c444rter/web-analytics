#!/bin/bash

# Set environment variable to fix fork() issue on macOS
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Change to the backend directory
cd backend

# Start the worker
python worker.py
