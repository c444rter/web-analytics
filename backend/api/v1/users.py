# api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db import crud, schemas, models
from core.security import create_access_token, verify_password
from db.database import SessionLocal
from core.deps import get_current_user

router = APIRouter(tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/json-token", response_model=schemas.Token, summary="User Login (JSON)")
async def json_login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    # Get the user by email
    user = crud.get_user_by_email(db, email=user_data.email)
    # Check the password
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create the access token
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup", response_model=schemas.UserOut, summary="User Sign-Up")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = crud.create_user(db, user)
    return new_user

@router.post("/token", response_model=schemas.Token, summary="User Login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut, summary="Get Current User Details")
def get_current_user_details(current_user: models.User = Depends(get_current_user)):
    """
    Get details of the currently authenticated user, including creation and update dates.
    """
    return current_user
