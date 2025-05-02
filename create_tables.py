import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateSchema
from sqlalchemy.exc import ProgrammingError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to sys.path so that your modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Base and models
from backend.db.models import Base
from backend.db import models  # This imports all models to register with Base

# Get the database URL from environment variable
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("ERROR: DATABASE_URL environment variable is not set.")
    print("Please set it to your Supabase connection string.")
    sys.exit(1)

print(f"Using DATABASE_URL: {database_url}")

# Create engine
engine = create_engine(database_url)

# Try to create the public schema if it doesn't exist
try:
    engine.execute(CreateSchema('public'))
    print("Created 'public' schema")
except ProgrammingError:
    print("'public' schema already exists")
except Exception as e:
    print(f"Error creating schema: {e}")

# Create all tables
print("Creating tables...")
Base.metadata.create_all(engine)
print("Tables created successfully!")

# List all tables that were created
print("\nCreated tables:")
for table in Base.metadata.sorted_tables:
    print(f"  - {table.name}")
