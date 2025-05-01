# security.py
import os
import sys
from datetime import datetime, timedelta
from typing import Union
from jose import JWTError, jwt
from passlib.context import CryptContext

# Load the SECRET_KEY from the environment with proper validation
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # In production, we should fail if SECRET_KEY is not set
    if os.getenv("ENVIRONMENT", "development").lower() == "production":
        print("ERROR: SECRET_KEY environment variable is not set. Exiting for security reasons.")
        sys.exit(1)
    else:
        # For development only, use a default key with a warning
        SECRET_KEY = "development_secret_key_not_for_production_use"
        print("WARNING: Using default SECRET_KEY for development. DO NOT use in production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
