# Segment 3: backend/app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Because we'll reference this container by the Docker service name "db"
DATABASE_URL = "postgresql://postgres:postgres@host.docker.internal:5432/analytics_dashboard"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
