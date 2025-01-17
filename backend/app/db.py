from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# For now, let's assume Postgres is at localhost; 
# we'll adjust for Docker later if needed:
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/analytics_dashboard"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
