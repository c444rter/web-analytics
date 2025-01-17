# app/routers/auth.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["auth"], prefix="/auth")

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(data: LoginRequest):
    """ Validate credentials and return user info or a token. """
    if data.email == "test@example.com" and data.password == "pass123":
        # A real app would query the database, verify password hash, etc.
        return {
            "id": 123,
            "email": data.email,
            "name": "Test User",
            "token": "fake_jwt_token_for_demo",
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
