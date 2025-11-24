from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_add_endpoint():
    response = client.post("/add", json={"x": 3, "y": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 8
    assert "calculation_id" in data


def test_subtract_endpoint():
    response = client.post("/subtract", json={"x": 10, "y": 4})
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 6
    assert "calculation_id" in data


def test_multiply_endpoint():
    response = client.post("/multiply", json={"x": 2, "y": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 10
    assert "calculation_id" in data


def test_divide_endpoint():
    response = client.post("/divide", json={"x": 10, "y": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 5
    assert "calculation_id" in data


def test_divide_by_zero_endpoint():
    response = client.post("/divide", json={"x": 10, "y": 0})
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot divide by zero"
