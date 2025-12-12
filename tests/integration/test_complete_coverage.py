"""Tests to achieve 100% code coverage"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db, Base, engine
from app.models import User, Calculation, SessionToken
from app.security import hash_password, create_access_token
from datetime import timedelta, datetime


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    return TestClient(app)


@pytest.fixture
def auth_user(test_db: Session):
    """Create an authenticated user and return token"""
    user = User(username="testuser", email="test@example.com", password_hash=hash_password("password123"))
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    client = TestClient(app)
    response = client.post("/users/login", json={"username_or_email": "testuser", "password": "password123"})
    token = response.json()["access_token"]
    return {"user": user, "token": token, "client": client}


def test_get_current_user_missing_header(client):
    """Test missing authorization header"""
    response = client.get("/users/me")
    assert response.status_code == 401
    assert "Missing Authorization header" in response.json()["detail"]


def test_get_current_user_invalid_header_format(client):
    """Test invalid authorization header format (not Bearer)"""
    response = client.get("/users/me", headers={"Authorization": "InvalidFormat token123"})
    assert response.status_code == 401
    assert "Invalid Authorization header" in response.json()["detail"]


def test_get_current_user_user_not_found(client, test_db):
    """Test when token has valid format but user doesn't exist"""
    # Create token with non-existent user_id
    fake_token = create_access_token({"user_id": 99999}, expires_delta=timedelta(minutes=30))
    response = client.get("/users/me", headers={"Authorization": f"Bearer {fake_token}"})
    assert response.status_code == 401
    assert "user not found" in response.json()["detail"].lower()


def test_update_user_no_changes(auth_user):
    """Test updating user with no actual changes"""
    client = auth_user["client"]
    token = auth_user["token"]
    
    # Update with empty payload
    response = client.put("/users/me", json={}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_update_user_duplicate_username(auth_user, test_db):
    """Test updating username to one that already exists"""
    client = auth_user["client"]
    token = auth_user["token"]
    
    # Create another user
    other_user = User(username="otheruser", email="other@example.com", password_hash=hash_password("pass"))
    test_db.add(other_user)
    test_db.commit()
    
    # Try to update to existing username
    response = client.put(
        "/users/me",
        json={"username": "otheruser", "email": "test@example.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


def test_math_endpoints_with_default_user(client):
    """Test math endpoints that create default_user"""
    # Test all math endpoints
    response = client.post("/add", json={"x": 5, "y": 3})
    assert response.status_code == 200
    assert response.json()["result"] == 8
    
    response = client.post("/subtract", json={"x": 10, "y": 4})
    assert response.status_code == 200
    assert response.json()["result"] == 6
    
    response = client.post("/multiply", json={"x": 3, "y": 4})
    assert response.status_code == 200
    assert response.json()["result"] == 12
    
    response = client.post("/divide", json={"x": 12, "y": 3})
    assert response.status_code == 200
    assert response.json()["result"] == 4


def test_calculation_invalid_operation_type(auth_user):
    """Test creating calculation with invalid operation type"""
    client = auth_user["client"]
    token = auth_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/calculations",
        json={"a": 5, "b": 3, "type": "invalid_operation"},
        headers=headers
    )
    # Should fail validation
    assert response.status_code in [400, 422]


def test_calculation_update_not_found(auth_user):
    """Test updating calculation that doesn't exist"""
    client = auth_user["client"]
    token = auth_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.put(
        "/calculations/99999",
        json={"a": 1, "b": 2, "type": "add"},
        headers=headers
    )
    assert response.status_code == 404


def test_calculation_delete_not_found(auth_user):
    """Test deleting calculation that doesn't exist"""
    client = auth_user["client"]
    token = auth_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.delete("/calculations/99999", headers=headers)
    assert response.status_code == 404


def test_database_get_db():
    """Test get_db generator function"""
    from app.database import get_db
    gen = get_db()
    db = next(gen)
    assert db is not None
    try:
        gen.close()
    except StopIteration:
        pass


def test_security_verify_password_bcrypt_truncation():
    """Test that password verification handles bcrypt 72-char limit"""
    from app.security import verify_password
    
    # Create a long password (> 72 chars)
    long_password = "a" * 100
    hashed = hash_password(long_password)
    
    # Verify the long password works
    assert verify_password(long_password, hashed)
    
    # Verify first 72 chars also work (bcrypt truncates)
    assert verify_password(long_password[:72], hashed)
    
    # Verify different password doesn't work
    assert not verify_password("wrong_password", hashed)
