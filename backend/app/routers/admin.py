# app/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/whitelist")
def get_whitelist(db: Session = Depends(get_db)):
    # e.g., query a Whitelist model or a column in your Users
    return ["test@example.com", "another@example.com"]

@router.post("/whitelist")
def add_whitelist(payload: dict, db: Session = Depends(get_db)):
    new_email = payload["email"]
    # logic to store in DB
    # return updated list
    return ["test@example.com", "another@example.com", new_email]
