# db/crud.py

from sqlalchemy.orm import Session
from db import models, schemas
from core.security import get_password_hash

# User CRUD
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Upload CRUD
def create_upload(db: Session, upload: schemas.UploadCreate, file_path: str, file_size: int, user_id: int, status: str = "pending"):
    db_upload = models.Upload(
        user_id=user_id,
        file_name=upload.file_name,
        file_path=file_path,
        file_size=file_size,
        status=status
    )
    db.add(db_upload)
    db.commit()
    db.refresh(db_upload)
    return db_upload

# Order and LineItem CRUD
def get_order_by_name_or_id(db: Session, user_id: int, shopify_id: str):
    return db.query(models.Order).filter(
        models.Order.user_id == user_id,
        models.Order.order_id == shopify_id
    ).first()

def create_order(db: Session, order_data: dict):
    db_order = models.Order(**order_data)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def create_line_item(db: Session, lineitem_data: dict):
    db_line_item = models.LineItem(**lineitem_data)
    db.add(db_line_item)
    db.commit()
    db.refresh(db_line_item)
    return db_line_item
