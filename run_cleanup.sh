#!/bin/bash
# Run Database Cleanup Script
# This script helps run the database cleanup operations with the correct environment variables

# Set the script to exit on error
set -e

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

# Check if the cleanup scripts exist
if [ ! -f "cleanup_failed_uploads.py" ] || [ ! -f "cleanup_db.sh" ]; then
  echo "Error: cleanup_failed_uploads.py or cleanup_db.sh not found in the current directory."
  exit 1
fi

# Make sure the scripts are executable
chmod +x cleanup_failed_uploads.py cleanup_db.sh

# Check if .env file exists
if [ ! -f ".env" ] && [ ! -f ".env.local" ] && [ ! -f "backend/.env" ] && [ ! -f "backend/.env.local" ]; then
  echo "Warning: No .env file found. You will need to set the environment variables manually."
  echo "Required environment variables:"
  echo "  - DATABASE_URL"
  echo "  - SUPABASE_URL"
  echo "  - SUPABASE_KEY"
  echo "  - SUPABASE_SERVICE_ROLE_KEY"
  echo "  - BUCKET_NAME"
  echo ""
  echo "Would you like to create a .env file now? (y/n)"
  read -r create_env
  
  if [[ "$create_env" =~ ^[Yy]$ ]]; then
    echo "Creating .env file..."
    echo "Enter your DATABASE_URL (e.g., postgresql://postgres:password@db.example.supabase.co:5432/postgres):"
    read -r database_url
    
    echo "Enter your SUPABASE_URL (e.g., https://example.supabase.co):"
    read -r supabase_url
    
    echo "Enter your SUPABASE_KEY (anon key):"
    read -r supabase_key
    
    echo "Enter your SUPABASE_SERVICE_ROLE_KEY:"
    read -r supabase_service_role_key
    
    echo "Enter your BUCKET_NAME (default: uploads):"
    read -r bucket_name
    bucket_name=${bucket_name:-uploads}
    
    # Create the .env file
    cat > .env << EOF
DATABASE_URL=${database_url}
SUPABASE_URL=${supabase_url}
SUPABASE_KEY=${supabase_key}
SUPABASE_SERVICE_ROLE_KEY=${supabase_service_role_key}
BUCKET_NAME=${bucket_name}
EOF
    
    echo ".env file created successfully."
  else
    echo "Continuing without creating .env file..."
  fi
fi

# Parse command line arguments
if [ $# -eq 0 ]; then
  show_help
  exit 0
fi

# Run the cleanup script with the provided arguments
echo "Running cleanup script with arguments: $*"
./cleanup_db.sh "$@"

# Check if the command was successful
if [ $? -eq 0 ]; then
  echo "Cleanup operation completed successfully."
else
  echo "Cleanup operation failed. Check the error messages above."
  exit 1
fi

# Provide next steps
echo ""
echo "Next Steps:"
echo "1. If you've deleted failed uploads, you may want to verify that they're gone:"
echo "   ./run_cleanup.sh list"
echo ""
echo "2. If you've reset stuck uploads, you may want to check their status:"
echo "   ./run_cleanup.sh list"
echo ""
echo "3. If you've cleaned up storage, you may want to verify with Supabase:"
echo "   - Log in to your Supabase Dashboard"
echo "   - Go to Storage → uploads"
echo "   - Verify that orphaned files are gone"
echo ""
echo "4. Once you're satisfied with the cleanup, you can push your changes to GitHub:"
echo "   git add ."
echo "   git commit -m \"Clean up database and storage\""
echo "   git push origin main"
echo ""
echo "5. Monitor the GitHub Actions workflow to ensure everything is working correctly."
