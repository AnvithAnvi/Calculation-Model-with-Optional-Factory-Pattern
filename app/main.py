# app/main.py
from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from app.database import Base, engine, get_db
from app.models import Calculation, User
from app.schemas import UserCreate, UserRead, CalculationCreate, CalculationRead, OperationType
from app.security import hash_password, verify_password, create_access_token, decode_access_token
from app.models import Calculation, User
from app.models import SessionToken
from fastapi import Header
from datetime import datetime, timedelta
from app.calculation_factory import CalculationFactory

# Make sure tables are created/updated
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Calculator with Factory Pattern")


# ---------- Helper: default user for calculations ----------

def get_or_create_default_user(db: Session) -> User:
    """
    Ensure there is at least one user in the DB that we can attach
    calculations to when the tests call /add,/subtract,/multiply,/divide
    without specifying a user.
    """
    user = db.query(User).filter(User.username == "default_user").first()
    if user:
        return user

    hashed = hash_password("defaultpassword")
    user = User(
        username="default_user",
        email="default@example.com",
        password_hash=hashed,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Dependency: get current user from Authorization header
def get_current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Check session token exists (simple revocation support)
    session = db.query(SessionToken).filter(SessionToken.token == token).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session revoked or not found")

    return user


def get_current_user_optional(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> User | None:
    """Optional version of get_current_user: returns None when no auth header provided.

    This allows legacy endpoints to remain usable without authentication while newer
    endpoints require an authenticated user.
    """
    if not authorization:
        return None
    try:
        return get_current_user(authorization, db)
    except HTTPException:
        return None



# ---------- User endpoints ----------

@app.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with a unique username and email.
    """
    # Check for existing username OR email
    existing_user = (
        db.query(User)
        .filter((User.email == user.email) | (User.username == user.username))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this username or email already exists",
        )

    hashed_pw = hash_password(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pw,
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="User with this username or email already exists",
        )

    return db_user


# New: user registration alias (keeps backward compatibility)
@app.post("/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Alias for creating users at /users/register."""
    return create_user(user, db)


# Login schema (simple)
class LoginRequest(BaseModel):
    username_or_email: str
    password: str


@app.post("/users/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Verify credentials and return a simple access token.

    This implementation uses a lightweight token (not JWT) for simplicity.
    """
    u = (
        db.query(User)
        .filter((User.username == payload.username_or_email) | (User.email == payload.username_or_email))
        .first()
    )
    if not u:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Create JWT access token
    expires = timedelta(minutes=60)
    token = create_access_token({"user_id": u.id}, expires_delta=expires)

    # Store session token for revocation support
    sess = SessionToken(token=token, user_id=u.id, created_at=datetime.utcnow(), expires_at=datetime.utcnow() + expires)
    db.add(sess)
    db.commit()

    return {"access_token": token, "token_type": "bearer", "user_id": u.id}


# ---------- Legacy Support Schemas ----------
# We keep this to ensure your existing tests (which send 'x' and 'y') still pass.

class CalcRequest(BaseModel):
    x: float
    y: float


# ---------- Calculator endpoints ----------

@app.post("/add")
def add_numbers(payload: CalcRequest, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)) -> Dict[str, float]:
    # 1. Use Factory for logic
    result = CalculationFactory.calculate(payload.x, payload.y, OperationType.ADD)

    # 2. Save to DB using NEW column names (a, b, type)
    # prefer authenticated user if available, otherwise fallback to default
    if getattr(current_user, 'id', None):
        user = current_user
    else:
        user = get_or_create_default_user(db)
    calc = Calculation(
        a=payload.x,      # Map x -> a
        b=payload.y,      # Map y -> b
        type=OperationType.ADD, # Store strict Enum type
        result=result,
        user_id=user.id,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}


@app.post("/subtract")
def subtract_numbers(
    payload: CalcRequest, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)
) -> Dict[str, float]:
    result = CalculationFactory.calculate(payload.x, payload.y, OperationType.SUBTRACT)

    if getattr(current_user, 'id', None):
        user = current_user
    else:
        user = get_or_create_default_user(db)
    calc = Calculation(
        a=payload.x,
        b=payload.y,
        type=OperationType.SUBTRACT,
        result=result,
        user_id=user.id,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}


@app.post("/multiply")
def multiply_numbers(
    payload: CalcRequest, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)
) -> Dict[str, float]:
    result = CalculationFactory.calculate(payload.x, payload.y, OperationType.MULTIPLY)

    if getattr(current_user, 'id', None):
        user = current_user
    else:
        user = get_or_create_default_user(db)
    calc = Calculation(
        a=payload.x,
        b=payload.y,
        type=OperationType.MULTIPLY,
        result=result,
        user_id=user.id,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}


@app.post("/divide")
def divide_numbers(
    payload: CalcRequest, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)
) -> Dict[str, float]:
    try:
        result = CalculationFactory.calculate(payload.x, payload.y, OperationType.DIVIDE)
    except ZeroDivisionError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot divide by zero",
        )

    if getattr(current_user, 'id', None):
        user = current_user
    else:
        user = get_or_create_default_user(db)
    calc = Calculation(
        a=payload.x,
        b=payload.y,
        type=OperationType.DIVIDE,
        result=result,
        user_id=user.id,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)

    return {"result": result, "calculation_id": calc.id}


# ---------- NEW Unified Endpoint (Requirement) ----------
# This satisfies the assignment requirement for "CalculationCreate" schema usage
# while allowing you to keep the specific endpoints above for your existing tests.

@app.post("/calculate", response_model=CalculationRead)
def perform_calculation(payload: CalculationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Unified endpoint using the Factory pattern and new Pydantic models.
    """
    try:
        result = CalculationFactory.calculate(payload.a, payload.b, payload.type)
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Cannot divide by zero")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if getattr(current_user, 'id', None):
        user = current_user
    else:
        user = get_or_create_default_user(db)
    
    calc_record = Calculation(
        a=payload.a,
        b=payload.b,
        type=payload.type,
        result=result,
        user_id=user.id
    )
    
    db.add(calc_record)
    db.commit()
    db.refresh(calc_record)

    return calc_record


# Dependency: get current user from Authorization header
def get_current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Check session token exists (simple revocation support)
    session = db.query(SessionToken).filter(SessionToken.token == token).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session revoked or not found")

    return user


# ---------- Calculation CRUD (BREAD) ----------
@app.get("/calculations", response_model=List[CalculationRead])
def list_calculations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Browse calculations owned by the authenticated user."""
    rows = db.query(Calculation).filter(Calculation.user_id == current_user.id).order_by(Calculation.id.asc()).all()
    return rows


@app.get("/calculations/{calculation_id}", response_model=CalculationRead)
def get_calculation(calculation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(Calculation).filter(Calculation.id == calculation_id, Calculation.user_id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return row


@app.post("/calculations", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def create_calculation(payload: CalculationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        result = CalculationFactory.calculate(payload.a, payload.b, payload.type)
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Cannot divide by zero")

    user = current_user
    calc = Calculation(a=payload.a, b=payload.b, type=payload.type, result=result, user_id=user.id)
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


@app.put("/calculations/{calculation_id}", response_model=CalculationRead)
def update_calculation(calculation_id: int, payload: CalculationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(Calculation).filter(Calculation.id == calculation_id, Calculation.user_id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Calculation not found")

    try:
        result = CalculationFactory.calculate(payload.a, payload.b, payload.type)
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Cannot divide by zero")

    row.a = payload.a
    row.b = payload.b
    row.type = payload.type
    row.result = result
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.delete("/calculations/{calculation_id}")
def delete_calculation(calculation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(Calculation).filter(Calculation.id == calculation_id, Calculation.user_id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Calculation not found")
    db.delete(row)
    db.commit()
    return {"detail": "deleted"}