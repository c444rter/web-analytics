# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import users, uploads, dashboard, analytics, projections, test_data
from dotenv import load_dotenv
import os

# Load environment variables from the .env file.
load_dotenv()

app = FastAPI()

# Define the list of frontend origins allowed. Adjust these values for your production domain(s).
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    # Allow Vercel preview deployments
    "https://*.vercel.app",
    # Add your custom domain when ready
    # "https://yourdomain.com",
]

# Add the CORS middleware to allow cross-origin requests from your frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # These origins can make requests.
    allow_credentials=True,       # Allow cookies and credentials.
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers.
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Shopify Analytics API (Multi-Line Orders)"}

# Include your API routes.
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(projections.router, prefix="/projections", tags=["projections"])
app.include_router(test_data.router, prefix="/test-data", tags=["test_data"])
