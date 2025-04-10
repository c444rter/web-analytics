# backend/tasks.py

from core.orders_processing import process_shopify_file
import traceback

def process_shopify_file_task(file_location: str, user_id: int, upload_id: int):
    """
    RQ Task: Process a Shopify file upload.
    Calls the existing order processing function and updates the Upload record status.
    """
    try:
        process_shopify_file(file_location, user_id, upload_id)
    except Exception as e:
        print(f"Error processing file {file_location} for user {user_id}, upload {upload_id}: {e}")
        traceback.print_exc()
