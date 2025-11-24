# app/security.py
import bcrypt

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
