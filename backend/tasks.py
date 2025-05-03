# backend/tasks.py

import os
import tempfile
import traceback
from core.orders_processing import process_shopify_file
from core.supabase_client import download_file_from_storage

def process_shopify_file_task(storage_path: str, user_id: int, upload_id: int):
    """
    RQ Task: Process a Shopify file upload from Supabase Storage.
    Downloads the file from Supabase, processes it, and cleans up.
    """
    # Create a temporary file to download the storage file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        print(f"Downloading file from Supabase Storage: {storage_path}")
        # Download file from Supabase Storage to temporary location - use admin key for background tasks
        download_file_from_storage(storage_path, temp_path, use_admin=True)
        
        # Process the file using the existing function
        process_shopify_file(temp_path, user_id, upload_id)
        
        # Clean up temporary file when done
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
        print(f"Error processing file {storage_path} for user {user_id}, upload {upload_id}: {e}")
        traceback.print_exc()
        
        # Clean up temporary file in case of error
        if os.path.exists(temp_path):
            os.remove(temp_path)
