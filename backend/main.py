# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import users, uploads, dashboard, analytics, projections, test_data
from dotenv import load_dotenv
import os
import time
from sqlalchemy.orm import Session
from core.deps import get_db
from core.redis_client import redis_client

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
    # Production domains
    "https://www.mydavids.com",
    "https://mydavids.com",
    # Allow all origins in development (comment out in production if needed)
    "*"
]

# Add the CORS middleware to allow cross-origin requests from your frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # These origins can make requests.
    allow_credentials=True,       # Allow cookies and credentials.
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers.
    expose_headers=["*"],         # Expose all headers to the browser
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Shopify Analytics API (Multi-Line Orders)"}

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint that verifies the application is running correctly.
    Checks database and Redis connections.
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "services": {
            "database": "unknown",
            "redis": "unknown"
        }
    }
    
    # Check database connection
    try:
        # Execute a simple query to check the database connection
        db.execute("SELECT 1").fetchone()
        health_status["services"]["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = f"error: {str(e)}"
    
    # Check Redis connection
    try:
        redis_client.ping()
        health_status["services"]["redis"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["redis"] = f"error: {str(e)}"
    
    # If any service is unhealthy, return a 503 status code
    if health_status["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    
    return health_status

# Include your API routes.
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(projections.router, prefix="/projections", tags=["projections"])
app.include_router(test_data.router, prefix="/test-data", tags=["test_data"])
