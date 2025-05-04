# api/v1/uploads.py

import os
import tempfile
import requests
import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from rq import Queue
from db import crud, schemas, models
from db.database import SessionLocal
from core.deps import get_current_user
from core.redis_client import redis_client
from core.supabase_client import upload_file_to_storage, get_file_url, get_upload_signed_url, BUCKET_NAME
from tasks import process_shopify_file_task
from typing import List

router = APIRouter(tags=["uploads"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.UploadOut, summary="Upload Order File (RQ Background)")
async def upload_file(
    file_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    allowed_extensions = {"zip", "csv", "json", "xls", "xlsx"}
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {ext}")

    contents = await file.read()
    file_size = len(contents)
    
    # Generate a unique storage path with timestamp to avoid conflicts
    timestamp = int(time.time())
    safe_filename = file.filename.replace(" ", "_")
    storage_path = f"{current_user.id}/{timestamp}_{safe_filename}"
    
    try:
        # Check Redis connection
        try:
            redis_test = redis_client.ping()
            print(f"Redis connection test: {redis_test}")
        except Exception as redis_error:
            print(f"Redis connection error: {str(redis_error)}")
            import traceback
            traceback.print_exc()
            # Continue anyway, we'll create the DB record even if Redis is down
        
        # Create database record with storage path first
        # This ensures we have a record even if the upload fails
        upload_data = schemas.UploadCreate(file_name=file_name)
        db_upload = crud.create_upload(
            db,
            upload=upload_data,
            file_path=f"pending://{BUCKET_NAME}/{storage_path}",  # Mark as pending
            file_size=file_size,
            user_id=current_user.id,
            status="pending"  # Set initial status
        )
        db.commit()  # Commit to ensure the record exists
        
        # Try to upload the file directly using our improved function
        try:
            print(f"Uploading file to storage path: {storage_path}")
            file_url = upload_file_to_storage(contents, storage_path, use_admin=True)
            print(f"File uploaded successfully to {file_url}")
            
            # Update the database record with the actual file path
            db_upload.file_path = file_url
            db_upload.status = "uploaded"  # File is uploaded but not processed yet
            db.commit()
        except Exception as upload_error:
            print(f"Direct upload failed: {str(upload_error)}")
            # Keep the pending status in the database
            # We'll still try to enqueue the job in case the file actually uploaded
        
        # Enqueue background task with storage path
        job_id_str = None
        try:
            q = Queue(connection=redis_client, default_timeout=3600)
            
            # Use the file_path from the database record, which contains the full URL
            # The worker will extract the actual path from this URL
            job = q.enqueue(process_shopify_file_task, db_upload.file_path, current_user.id, db_upload.id)
            
            # Decode the job ID to a string before returning it
            job_id_str = job.get_id().decode() if isinstance(job.get_id(), bytes) else job.get_id()
            
            # Update the database record with the job ID
            db_upload.status = "processing"  # Update status to processing
            db.commit()
            
            print(f"Background job enqueued with ID: {job_id_str} for file_path: {db_upload.file_path}")
        except Exception as redis_error:
            print(f"Failed to enqueue background job: {str(redis_error)}")
            # If we can't enqueue the job, update the status
            db_upload.status = "upload_complete"  # File is uploaded but processing not started
            db.commit()

        # Return both the DB upload_id and the Redis job ID (if available)
        return {
            "id": db_upload.id,
            "file_name": db_upload.file_name,
            "file_path": db_upload.file_path,
            "file_size": db_upload.file_size,
            "uploaded_at": db_upload.uploaded_at,
            "status": db_upload.status,
            "job_id": job_id_str,
            "upload_id": db_upload.id,
            "message": "File upload initiated. Check status endpoint for progress."
        }
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to create a failed upload record if we haven't already
        try:
            if 'db_upload' not in locals():
                upload_data = schemas.UploadCreate(file_name=file_name)
                db_upload = crud.create_upload(
                    db,
                    upload=upload_data,
                    file_path=f"failed://{file_name}",
                    file_size=file_size,
                    user_id=current_user.id,
                    status="failed"
                )
                db.commit()
                
                return {
                    "id": db_upload.id,
                    "file_name": db_upload.file_name,
                    "file_path": db_upload.file_path,
                    "file_size": db_upload.file_size,
                    "uploaded_at": db_upload.uploaded_at,
                    "status": "failed",
                    "upload_id": db_upload.id,
                    "error": str(e),
                    "message": "Upload failed, but record created for tracking."
                }
        except Exception as db_error:
            print(f"Failed to create error record: {str(db_error)}")
            
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/status/{upload_id}", summary="Check DB-based Upload Status")
def get_upload_status(upload_id: int, db: Session = Depends(get_db)):
    """
    Returns status, total_rows, records_processed, and a percent
    for the DB upload record. This is what the front end can poll to get
    real-time progress (0-100%).
    """
    upload = db.query(models.Upload).filter(models.Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    percent = 0
    if upload.status == "completed":
        percent = 100
    elif upload.status == "failed":
        percent = 0
    elif upload.status == "pending" or upload.status == "uploaded":
        percent = 10  # Show some progress even at the beginning
    elif upload.total_rows > 0:
        percent = int((upload.records_processed / upload.total_rows) * 100)
        # Cap at 99% until status is "completed"
        if percent >= 99 and upload.status != "completed":
            percent = 99

    # Ensure that upload_id is a string (in case it was returned as bytes)
    upload_id_str = str(upload.id) if isinstance(upload.id, bytes) else upload.id

    # Add a message based on status
    message = ""
    if upload.status == "pending":
        message = "Upload pending..."
    elif upload.status == "uploaded":
        message = "File uploaded, waiting to start processing..."
    elif upload.status == "processing":
        message = f"Processing: {percent}% complete"
    elif upload.status == "completed":
        message = "Processing completed successfully!"
    elif upload.status == "failed":
        message = "Processing failed. Please try again."

    return {
        "status": upload.status,
        "total_rows": upload.total_rows,
        "records_processed": upload.records_processed,
        "percent": percent,
        "upload_id": upload_id_str,  # Return the upload_id as a string
        "message": message
    }

@router.get("/history")
async def get_upload_history(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        # Query uploads for the current user
        uploads = db.query(models.Upload).filter(models.Upload.user_id == current_user.id).all()
        
        # Generate signed URLs for any Supabase paths
        for upload in uploads:
            if upload.file_path and upload.file_path.startswith("supabase://"):
                # Extract the storage path from the URL
                storage_path = upload.file_path.replace(f"supabase://{os.environ.get('BUCKET_NAME', 'uploads')}/", "")
                # Generate a signed URL with admin key for downloads
                upload.download_url = get_file_url(storage_path, use_admin=True)
            else:
                upload.download_url = None
                
        return {"uploads": uploads}
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
