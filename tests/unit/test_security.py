# tests/unit/test_security.py
from app.security import hash_password, verify_password

def test_password_hash_and_verify():
    password = "supersecret"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_long_password_truncated_for_bcrypt():
    long_password = "a" * 100
    hashed = hash_password(long_password)

    # bcrypt only sees first 72 'a's, so verifying 72 should still work
    assert verify_password("a" * 72, hashed)
