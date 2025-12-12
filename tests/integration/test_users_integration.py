# tests/integration/test_users_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine


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


def test_create_user_success(client):
    payload = {
        "username": "integrationuser",
        "email": "integration@example.com",
        "password": "password123",
    }
    res = client.post("/users/", json=payload)

    assert res.status_code == 201
    data = res.json()

    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "created_at" in data


def test_create_user_duplicate_email(client):
    payload1 = {
        "username": "user1",
        "email": "dupe@example.com",
        "password": "password123",
    }
    payload2 = {
        "username": "user2",   # different username
        "email": "dupe@example.com",  # same email
        "password": "password123",
    }

    r1 = client.post("/users/", json=payload1)
    assert r1.status_code == 201

    r2 = client.post("/users/", json=payload2)
    assert r2.status_code == 400
    assert "exists" in r2.json()["detail"].lower()


def test_create_user_duplicate_username(client):
    payload1 = {
        "username": "sameuser",
        "email": "email1@example.com",
        "password": "password123",
    }
    payload2 = {
        "username": "sameuser",  # same username
        "email": "email2@example.com",
        "password": "password123",
    }

    r1 = client.post("/users/", json=payload1)
    assert r1.status_code == 201

    r2 = client.post("/users/", json=payload2)
    assert r2.status_code == 400
    assert "exists" in r2.json()["detail"].lower()
