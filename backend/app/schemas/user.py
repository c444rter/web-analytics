# app/schemas/user.py
from pydantic import BaseModel, ConfigDict, EmailStr

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
