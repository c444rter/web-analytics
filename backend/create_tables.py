import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import the Base and models
from db.models import Base
from db import models

def create_tables():
    # Get the database URL from environment variables
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("DATABASE_URL environment variable not set")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test the connection
        session.execute(text("SELECT 1"))
        
        print("Database connection successful and tables created")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    create_tables()
