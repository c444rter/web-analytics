# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users
from app.db import Base, engine

app = FastAPI()

origins = ["*"]  # EXACT origin to match your Next.js dev URL
# or for local dev you can do: origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "FastAPI with CORS enabled"}
