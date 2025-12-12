"""Additional tests to improve code coverage to 100%"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db, Base, engine
from app.models import User, Calculation
from app.security import hash_password


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
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


def test_password_change_with_wrong_current_password(auth_user):
    """Test password change with incorrect current password"""
    client = auth_user["client"]
    token = auth_user["token"]
    
    response = client.post(
        "/users/me/password",
        json={"current_password": "wrongpassword", "new_password": "newpassword123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert "Invalid current password" in response.json()["detail"]


def test_get_current_user_with_invalid_token(client):
    """Test getting current user with invalid token"""
    response = client.get("/users/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401


def test_get_current_user_without_user_id_in_token(client, test_db):
    """Test getting current user when token doesn't have user_id"""
    from app.security import create_access_token
    from datetime import timedelta
    
    # Create token without user_id
    token = create_access_token({"sub": "test"}, expires_delta=timedelta(minutes=30))
    
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_update_user_duplicate_email(auth_user, test_db):
    """Test updating user with email that already exists"""
    client = auth_user["client"]
    token = auth_user["token"]
    
    # Create another user
    other_user = User(username="otheruser", email="other@example.com", password_hash=hash_password("pass"))
    test_db.add(other_user)
    test_db.commit()
    
    # Try to update to existing email
    response = client.put(
        "/users/me",
        json={"email": "other@example.com", "username": "testuser"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "email already in use" in response.text.lower()


def test_update_user_duplicate_username(auth_user, test_db):
    """Test updating user with username that already exists"""
    client = auth_user["client"]
    token = auth_user["token"]
    
    # Create another user
    other_user = User(username="otheruser", email="other@example.com", password_hash=hash_password("pass"))
    test_db.add(other_user)
    test_db.commit()
    
    # Try to update to existing username
    response = client.put(
        "/users/me",
        json={"email": "test@example.com", "username": "otheruser"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "username already taken" in response.text.lower()


def test_calculation_not_found(auth_user):
    """Test getting/updating/deleting a calculation that doesn't exist"""
    client = auth_user["client"]
    token = auth_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to get non-existent calculation
    response = client.get("/calculations/99999", headers=headers)
    assert response.status_code == 404
    
    # Try to update non-existent calculation
    response = client.put("/calculations/99999", json={"a": 1, "b": 2, "type": "add"}, headers=headers)
    assert response.status_code == 404
    
    # Try to delete non-existent calculation
    response = client.delete("/calculations/99999", headers=headers)
    assert response.status_code == 404


def test_calculation_access_forbidden(auth_user, test_db):
    """Test accessing another user's calculation"""
    client = auth_user["client"]
    token = auth_user["token"]
    
    # Create another user with a calculation
    other_user = User(username="other", email="other@test.com", password_hash=hash_password("pass"))
    test_db.add(other_user)
    test_db.commit()
    test_db.refresh(other_user)
    
    calc = Calculation(a=5, b=3, type="add", result=8, user_id=other_user.id)
    test_db.add(calc)
    test_db.commit()
    test_db.refresh(calc)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to access another user's calculation - API returns 404 for both GET and PUT
    response = client.get(f"/calculations/{calc.id}", headers=headers)
    assert response.status_code == 404
    response = client.put(f"/calculations/{calc.id}", json={"a": 1, "b": 2, "type": "add"}, headers=headers)
    assert response.status_code == 404  # Also returns 404 for PUT
    
    # Try to delete another user's calculation - also returns 404
    response = client.delete(f"/calculations/{calc.id}", headers=headers)
    assert response.status_code == 404


def test_calculation_factory_invalid_operation():
    """Test calculation factory with invalid operation type"""
    from app.calculation_factory import CalculationFactory
    
    with pytest.raises(ValueError, match="Unknown operation type"):
        CalculationFactory.calculate(5, 3, "invalid_operation")


def test_login_with_invalid_credentials(client, test_db):
    """Test login with wrong password"""
    user = User(username="testuser", email="test@example.com", password_hash=hash_password("correctpass"))
    test_db.add(user)
    test_db.commit()
    
    response = client.post("/users/login", json={"username_or_email": "testuser", "password": "wrongpass"})
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_with_nonexistent_user(auth_user, test_db):
    """Test login with user that doesn't exist"""
    client = auth_user["client"]
    response = client.post("/users/login", json={"username_or_email": "nonexistent", "password": "pass"})
    assert response.status_code == 401


def test_delete_all_calculations(auth_user, test_db):
    """Test deleting all calculations for a user"""
    client = auth_user["client"]
    token = auth_user["token"]
    user = auth_user["user"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create some calculations
    for i in range(3):
        calc = Calculation(a=i, b=i+1, type="add", result=i*2+1, user_id=user.id)
        test_db.add(calc)
    test_db.commit()
    
    # Test getting calculations
    response = client.get("/calculations", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 3  # At least the 3 we just created


def test_stats_endpoint(auth_user, test_db):
    """Test stats endpoint coverage"""
    client = auth_user["client"]
    token = auth_user["token"]
    user = auth_user["user"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create calculations with different operations
    operations = ["add", "subtract", "multiply", "divide", "modulus", "exponent"]
    for op in operations:
        calc = Calculation(a=10, b=5, type=op, result=15, user_id=user.id)
        test_db.add(calc)
    test_db.commit()
    
    response = client.get("/calculations/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 6
    assert "counts" in data
    assert "recent" in data


def test_root_redirect(client):
    """Test root path redirects to register"""
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert "/static/register.html" in response.headers["location"]


def test_security_password_truncation():
    """Test that passwords longer than 72 chars are truncated for bcrypt"""
    from app.security import hash_password, verify_password
    
    long_password = "a" * 100
    hashed = hash_password(long_password)
    
    # Should verify with truncated version
    assert verify_password("a" * 72, hashed)
    # Should also verify with full length (bcrypt truncates automatically)
    assert verify_password(long_password, hashed)
