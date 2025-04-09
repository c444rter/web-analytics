# core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from db import crud, models
from db.database import SessionLocal
from core.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print("Received token:", token)  # Debug log
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Decoded payload:", payload)  # Debug log
        user_id: str = payload.get("sub")
        if user_id is None:
            print("No subject found in token")
            raise credentials_exception
    except JWTError as e:
        print("JWT decoding error:", e)
        raise credentials_exception
    user = crud.get_user(db, user_id=int(user_id))
    if user is None:
        print("No user found with id:", user_id)
        raise credentials_exception
    return user

