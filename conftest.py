# conftest.py
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Default to SQLite in-memory for fast, isolated tests.
# But allow overriding via DATABASE_URL (e.g., GitHub Actions/postgres container).
# Use a file-backed SQLite DB for shared access across modules during tests.
# This avoids issues where multiple engines each create their own in-memory DB.
DEFAULT_TEST_DB = "sqlite:///./test.db"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_TEST_DB)

# If DATABASE_URL wasn't provided, set it in the environment so app modules
# (which import app.database at import time) use the same DB during tests.
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = DATABASE_URL

# For SQLite in-memory with multiple threads (TestClient), we need this arg.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import Base after DATABASE_URL is set so that app.database uses the test DB
from app.database import Base

# Create tables once for the entire test session. Using a file-backed SQLite DB
# means multiple engines/connections will see the same schema.
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Provide a SQLAlchemy session for tests. Each test gets a fresh session.
    We avoid dropping the schema between tests so that endpoints created at
    import time (app.main) can rely on the same tables.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # Rollback any open transaction and close the connection.
        db.rollback()
        db.close()
