import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use DATABASE_URL from environment (GitHub Actions sets this)
# Default to in-memory SQLite for local test runs unless DATABASE_URL is set
# Use PostgreSQL in CI by setting the DATABASE_URL environment variable.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
# Default to a file-backed SQLite for local development/tests unless DATABASE_URL is set
# In-memory SQLite (sqlite:///:memory:) does not persist across connections and causes
# "no such table" errors when the app opens new DB connections. Use a file-based DB
# so tables created at startup persist.

# SQLAlchemy engine
# If using SQLite, allow connections from multiple threads (useful for TestClient)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
