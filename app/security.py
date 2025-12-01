# app/security.py
import bcrypt
import os
import jwt
from datetime import datetime, timedelta

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

MAX_BCRYPT_BYTES = 72

def _truncate_password(password: str) -> bytes:
    """
    Ensure password is at most 72 bytes, as required by bcrypt.
    """
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > MAX_BCRYPT_BYTES:
        pw_bytes = pw_bytes[:MAX_BCRYPT_BYTES]
    return pw_bytes


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    """
    pw_bytes = _truncate_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_bytes, salt)
    # store as utf-8 string
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """
    pw_bytes = _truncate_password(plain_password)
    return bcrypt.checkpw(pw_bytes, hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise
    except Exception:
        raise
