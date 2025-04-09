# api/v1/uploads.py

import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from rq import Queue
from db import crud, schemas, models
from db.database import SessionLocal
from core.deps import get_current_user
from core.redis_client import redis_client
from tasks import process_shopify_file_task
from typing import List

router = APIRouter(tags=["uploads"])

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    contents = await file.read()
    with open(file_location, "wb") as buffer:
        buffer.write(contents)

    file_size = len(contents)
    upload_data = schemas.UploadCreate(file_name=file_name)
    db_upload = crud.create_upload(
        db,
        upload=upload_data,
        file_path=file_location,
        file_size=file_size,
        user_id=current_user.id
    )

    # Enqueue the background task
    q = Queue(connection=redis_client, default_timeout=3600)
    job = q.enqueue(process_shopify_file_task, file_location, current_user.id, db_upload.id)

    # Decode the job ID to a string before returning it
    job_id_str = job.get_id().decode() if isinstance(job.get_id(), bytes) else job.get_id()

    # Return both the DB upload_id and the Redis job ID
    return {
        "id": db_upload.id,
        "file_name": db_upload.file_name,
        "file_path": db_upload.file_path,
        "file_size": db_upload.file_size,
        "uploaded_at": db_upload.uploaded_at,
        "status": db_upload.status,
        "job_id": job_id_str,        # Ensure job ID is a string
        "upload_id": db_upload.id      # DB-based upload ID
    }


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
    if upload.total_rows > 0:
        percent = int((upload.records_processed / upload.total_rows) * 100)

    # Ensure that upload_id is a string (in case it was returned as bytes)
    upload_id_str = str(upload.id) if isinstance(upload.id, bytes) else upload.id

    return {
        "status": upload.status,
        "total_rows": upload.total_rows,
        "records_processed": upload.records_processed,
        "percent": percent,
        "upload_id": upload_id_str  # Return the upload_id as a string
    }

@router.get("/history")
async def get_upload_history(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        # Query uploads for the current user
        uploads = db.query(models.Upload).filter(models.Upload.user_id == current_user.id).all()
        return {"uploads": uploads}
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
