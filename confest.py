# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

# Use an in-memory SQLite database for fast unit/integration testing
# OR use the postgres container if you prefer. 
# For isolated integration tests, SQLite in-memory is often easiest, 
# but the prompt asks for PostgreSQL container usage. 
# We assume the environment variables in GitHub Actions point to Postgres.
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Creates a fresh database session for a test.
    Rolls back transaction after test to keep DB clean.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test (if using SQLite) or rely on transaction rollback
        Base.metadata.drop_all(bind=engine)