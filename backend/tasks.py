# backend/tasks.py

import os
import tempfile
import traceback
import time
from core.orders_processing import process_shopify_file
from core.supabase_client import download_file_from_storage, BUCKET_NAME

def process_test_task(test_data: str):
    """
    A simple test task for CI/CD pipeline worker testing.
    This function simply logs the test data and returns it.
    """
    print(f"Processing test task with data: {test_data}")
    # Simulate some work
    time.sleep(2)
    print(f"Test task completed for data: {test_data}")
    return test_data

def process_shopify_file_task(storage_path: str, user_id: int, upload_id: int):
    """
    RQ Task: Process a Shopify file upload from Supabase Storage.
    Downloads the file from Supabase, processes it, and cleans up.
    """
    # Create a temporary file to download the storage file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        print(f"Processing task for storage_path: {storage_path}, user_id: {user_id}, upload_id: {upload_id}")
        
        # Extract the actual storage path if it's a full URL
        actual_path = storage_path
        if storage_path.startswith(f"supabase://{BUCKET_NAME}/"):
            actual_path = storage_path.replace(f"supabase://{BUCKET_NAME}/", "")
            print(f"Extracted actual path from URL: {actual_path}")
        
        print(f"Downloading file from Supabase Storage: {actual_path}")
        # Download file from Supabase Storage to temporary location - use admin key for background tasks
        download_file_from_storage(actual_path, temp_path, use_admin=True)
        
        # Process the file using the existing function
        print(f"Processing file: {temp_path}")
        process_shopify_file(temp_path, user_id, upload_id)
        
        # Clean up temporary file when done
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Temporary file removed: {temp_path}")
            
        # Ensure the upload status is updated to completed
        from db.database import SessionLocal
        from db import models
        db = SessionLocal()
        try:
            upload = db.query(models.Upload).filter(models.Upload.id == upload_id).first()
            if upload:
                upload.status = "completed"
                db.commit()
                print(f"Upload status updated to 'completed' for upload_id: {upload_id}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error processing file {storage_path} for user {user_id}, upload {upload_id}: {e}")
        traceback.print_exc()
        
        # Update status to failed in case of error
        from db.database import SessionLocal
        from db import models
        db = SessionLocal()
        try:
            upload = db.query(models.Upload).filter(models.Upload.id == upload_id).first()
            if upload:
                upload.status = "failed"
                db.commit()
                print(f"Upload status updated to 'failed' for upload_id: {upload_id}")
        finally:
            db.close()
        
        # Clean up temporary file in case of error
        if os.path.exists(temp_path):
            os.remove(temp_path)
