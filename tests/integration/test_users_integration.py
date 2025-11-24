# tests/integration/test_users_integration.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user_success():
    payload = {
        "username": "integrationuser",
        "email": "integration@example.com",
        "password": "password123",
    }
    res = client.post("/users/", json=payload)

    #print("DEBUG create_user_success:", res.status_code, res.json())

    assert res.status_code == 201
    data = res.json()

    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "created_at" in data

def test_create_user_duplicate_email():
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
