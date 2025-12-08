import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use DATABASE_URL from environment (GitHub Actions sets this)
# Default to in-memory SQLite for local test runs unless DATABASE_URL is set
# Use PostgreSQL in CI by setting the DATABASE_URL environment variable.
# Prefer an on-disk sqlite DB by default to avoid cross-connection in-memory issues
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tmp_test.db")

# If using a file-backed sqlite DB, ensure the file exists and is writable so
# tests and the running app can create/modify tables. Some CI or local copies
# of `test.db` may be checked in with restrictive permissions which cause
# "attempt to write a readonly database" errors during test runs.
if DATABASE_URL.startswith("sqlite:///"):
    try:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        db_file = Path(db_path)
        if not db_file.parent.exists():
            db_file.parent.mkdir(parents=True, exist_ok=True)
        if not db_file.exists():
            db_file.touch()
        try:
            db_file.chmod(0o666)
        except Exception:
            pass
    except Exception:
        pass
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
