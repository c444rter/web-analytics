#!/bin/bash
# Database Cleanup Script for Web Analytics
# This script provides a simple interface for running database cleanup operations

# Set the script to exit on error
set -e

# Load environment variables
if [ -f .env ]; then
  source .env
elif [ -f .env.local ]; then
  source .env.local
elif [ -f backend/.env ]; then
  source backend/.env
elif [ -f backend/.env.local ]; then
  source backend/.env.local
fi

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ]; then
  echo "Error: DATABASE_URL environment variable is not set."
  echo "Please set it in .env, .env.local, backend/.env, or backend/.env.local"
  exit 1
fi

# Function to display help
show_help() {
  echo "Usage: $0 [OPTION]"
  echo "Run database cleanup operations for Web Analytics."
  echo ""
  echo "Options:"
  echo "  list                List all uploads with their status"
  echo "  delete ID           Delete a specific upload by ID"
  echo "  delete-failed       Delete all failed uploads"
  echo "  reset-stuck         Reset the status of stuck uploads"
  echo "  cleanup-storage     Clean up orphaned storage files"
  echo "  all                 Run all cleanup operations (delete-failed, reset-stuck, cleanup-storage)"
  echo "  dry-run             Show what would be done without making changes"
  echo "  help                Display this help message"
  echo ""
  echo "Examples:"
  echo "  $0 list"
  echo "  $0 delete 123"
  echo "  $0 delete-failed"
  echo "  $0 all"
  echo "  $0 delete-failed --dry-run"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
  echo "Error: python3 is not installed or not in PATH."
  exit 1
fi

# Check if the cleanup script exists
if [ ! -f "cleanup_failed_uploads.py" ]; then
  echo "Error: cleanup_failed_uploads.py not found in the current directory."
  exit 1
fi

# Make sure the script is executable
chmod +x cleanup_failed_uploads.py

# Parse command line arguments
if [ $# -eq 0 ]; then
  show_help
  exit 0
fi

DRY_RUN=""
if [[ "$*" == *"--dry-run"* ]]; then
  DRY_RUN="--dry-run"
  # Remove --dry-run from the arguments
  set -- "${@/--dry-run/}"
fi

case "$1" in
  list)
    echo "Listing all uploads..."
    python3 cleanup_failed_uploads.py --list
    ;;
  delete)
    if [ -z "$2" ]; then
      echo "Error: Please provide an upload ID to delete."
      exit 1
    fi
    echo "Deleting upload with ID $2..."
    python3 cleanup_failed_uploads.py --delete-id "$2" $DRY_RUN
    ;;
  delete-failed)
    echo "Deleting all failed uploads..."
    python3 cleanup_failed_uploads.py --delete-failed $DRY_RUN
    ;;
  reset-stuck)
    echo "Resetting stuck uploads..."
    python3 cleanup_failed_uploads.py --reset-stuck $DRY_RUN
    ;;
  cleanup-storage)
    echo "Cleaning up orphaned storage files..."
    python3 cleanup_failed_uploads.py --cleanup-storage $DRY_RUN
    ;;
  all)
    echo "Running all cleanup operations..."
    python3 cleanup_failed_uploads.py --delete-failed --reset-stuck --cleanup-storage $DRY_RUN
    ;;
  help)
    show_help
    ;;
  *)
    echo "Error: Unknown option '$1'"
    show_help
    exit 1
    ;;
esac

echo "Done!"
