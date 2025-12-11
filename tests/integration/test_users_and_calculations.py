from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)


def test_register_and_login_flow():
    suffix = uuid.uuid4().hex[:8]
    username = f"int_user_{suffix}"
    email = f"{username}@example.com"
    payload = {
        "username": username,
        "email": email,
        "password": "strongpassword",
    }
    r = client.post("/users/register", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]

    # login with username
    login_payload = {"username_or_email": payload["username"], "password": payload["password"]}
    r2 = client.post("/users/login", json=login_payload)
    assert r2.status_code == 200
    t = r2.json()
    assert "access_token" in t
    assert t["user_id"] == data["id"]


def test_calculation_bread():
    # create a fresh user and login to get token
    import uuid
    suffix = uuid.uuid4().hex[:8]
    username = f"calc_user_{suffix}"
    email = f"{username}@example.com"
    reg = client.post("/users/register", json={"username": username, "email": email, "password": "strongpassword"})
    assert reg.status_code == 201
    login_payload = {"username_or_email": username, "password": "strongpassword"}
    r_login = client.post("/users/login", json=login_payload)
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create
    create_payload = {"a": 10, "b": 5, "type": "add"}
    r = client.post("/calculations", json=create_payload, headers=headers)
    assert r.status_code == 201
    c = r.json()
    assert c["a"] == 10
    assert c["b"] == 5
    assert c["result"] == 15
    calc_id = c["id"]

    # browse/list
    r2 = client.get("/calculations", headers=headers)
    assert r2.status_code == 200
    arr = r2.json()
    assert any(x["id"] == calc_id for x in arr)

    # read
    r3 = client.get(f"/calculations/{calc_id}", headers=headers)
    assert r3.status_code == 200
    one = r3.json()
    assert one["id"] == calc_id

    # update (change to multiply 2 * 3)
    upd_payload = {"a": 2, "b": 3, "type": "multiply"}
    r4 = client.put(f"/calculations/{calc_id}", json=upd_payload, headers=headers)
    assert r4.status_code == 200
    updated = r4.json()
    assert updated["result"] == 6

    # delete
    r5 = client.delete(f"/calculations/{calc_id}", headers=headers)
    assert r5.status_code == 200
    assert r5.json()["detail"] == "deleted"


def test_modulus_and_exponent_operations():
    # create a fresh user and login to get token
    import uuid
    suffix = uuid.uuid4().hex[:8]
    username = f"op_user_{suffix}"
    email = f"{username}@example.com"
    reg = client.post("/users/register", json={"username": username, "email": email, "password": "strongpassword"})
    assert reg.status_code == 201
    r_login = client.post("/users/login", json={"username_or_email": username, "password": "strongpassword"})
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # modulus
    r_mod = client.post("/calculations", json={"a": 10, "b": 3, "type": "modulus"}, headers=headers)
    assert r_mod.status_code == 201
    assert r_mod.json()["result"] == 1

    # exponent
    r_pow = client.post("/calculations", json={"a": 2, "b": 5, "type": "exponent"}, headers=headers)
    assert r_pow.status_code == 201
    assert r_pow.json()["result"] == 32


def test_invalid_division_returns_error():
    # create a fresh user and login to get token
    import uuid
    suffix = uuid.uuid4().hex[:8]
    username = f"div_user_{suffix}"
    email = f"{username}@example.com"
    reg = client.post("/users/register", json={"username": username, "email": email, "password": "strongpassword"})
    assert reg.status_code == 201
    login_payload = {"username_or_email": username, "password": "strongpassword"}
    r_login = client.post("/users/login", json=login_payload)
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"a": 3, "b": 0, "type": "divide"}
    r = client.post("/calculations", json=payload, headers=headers)
    # Should reject division by zero (Pydantic validation -> 422 or app -> 400)
    assert r.status_code in (400, 422)
    detail = r.json().get("detail")
    if isinstance(detail, list):
        # FastAPI validation errors are a list of error objects
        detail_str = str(detail).lower()
    else:
        detail_str = str(detail).lower()

    assert "divide by zero" in detail_str or "cannot divide by zero" in detail_str
