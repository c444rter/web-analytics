import os
import sys
import tempfile
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

from db.database import SessionLocal
from db import models
from core.supabase_client import download_file_from_storage, BUCKET_NAME
from core.orders_processing import process_shopify_file

# Load environment variables from .env file
env_path = Path(__file__).parent / 'backend' / '.env'
load_dotenv(dotenv_path=env_path)

# Print environment variables for debugging
print(f"SUPABASE_URL: {os.environ.get('SUPABASE_URL')}")
print(f"BUCKET_NAME: {os.environ.get('BUCKET_NAME')}")

def debug_process_file(upload_id):
    """
    Debug function to process a file directly without using Redis
    """
    db = SessionLocal()
    try:
        # Get the upload record
        upload = db.query(models.Upload).filter(models.Upload.id == upload_id).first()
        if not upload:
            print(f"No upload found with ID {upload_id}")
            return
        
        print(f"Found upload: {upload.id}, file_path: {upload.file_path}, user_id: {upload.user_id}")
        
        # Extract the actual storage path if it's a full URL
        storage_path = upload.file_path
        actual_path = storage_path
        if storage_path.startswith(f"supabase://{BUCKET_NAME}/"):
            actual_path = storage_path.replace(f"supabase://{BUCKET_NAME}/", "")
            print(f"Extracted actual path from URL: {actual_path}")
        
        # Create a temporary file to download the storage file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            print(f"Downloading file from Supabase Storage: {actual_path}")
            # Download file from Supabase Storage to temporary location
            download_file_from_storage(actual_path, temp_path, use_admin=True)
            
            print(f"File downloaded to {temp_path}")
            
            # Check if the file exists and has content
            if os.path.exists(temp_path):
                file_size = os.path.getsize(temp_path)
                print(f"File exists, size: {file_size} bytes")
                
                # Read the first few lines of the file to verify content
                with open(temp_path, 'r') as f:
                    first_lines = [next(f) for _ in range(5)]
                    print("First few lines of the file:")
                    for line in first_lines:
                        print(f"  {line.strip()}")
                
                # Try to process the file
                print("\nAttempting to process the file...")
                try:
                    process_shopify_file(temp_path, upload.user_id, upload.id)
                    print("File processed successfully!")
                except Exception as e:
                    print(f"Error processing file: {e}")
                    traceback.print_exc()
            else:
                print(f"File does not exist at {temp_path}")
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"Temporary file removed: {temp_path}")
                
        except Exception as e:
            print(f"Error downloading file {storage_path}: {e}")
            traceback.print_exc()
            
            # Clean up temporary file in case of error
            if os.path.exists(temp_path):
                os.remove(temp_path)
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_worker.py <upload_id>")
        sys.exit(1)
    
    upload_id = int(sys.argv[1])
    debug_process_file(upload_id)
