# app/main.py
from typing import Dict

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from app.database import Base, engine, get_db
from app.models import Calculation, User
from app.schemas import UserCreate, UserRead, CalculationCreate, CalculationRead, OperationType
from app.security import hash_password
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


# ---------- Legacy Support Schemas ----------
# We keep this to ensure your existing tests (which send 'x' and 'y') still pass.

class CalcRequest(BaseModel):
    x: float
    y: float


# ---------- Calculator endpoints ----------

@app.post("/add")
def add_numbers(payload: CalcRequest, db: Session = Depends(get_db)) -> Dict[str, float]:
    # 1. Use Factory for logic
    result = CalculationFactory.calculate(payload.x, payload.y, OperationType.ADD)

    # 2. Save to DB using NEW column names (a, b, type)
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
    payload: CalcRequest, db: Session = Depends(get_db)
) -> Dict[str, float]:
    result = CalculationFactory.calculate(payload.x, payload.y, OperationType.SUBTRACT)

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
    payload: CalcRequest, db: Session = Depends(get_db)
) -> Dict[str, float]:
    result = CalculationFactory.calculate(payload.x, payload.y, OperationType.MULTIPLY)

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
    payload: CalcRequest, db: Session = Depends(get_db)
) -> Dict[str, float]:
    try:
        result = CalculationFactory.calculate(payload.x, payload.y, OperationType.DIVIDE)
    except ZeroDivisionError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot divide by zero",
        )

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
def perform_calculation(payload: CalculationCreate, db: Session = Depends(get_db)):
    """
    Unified endpoint using the Factory pattern and new Pydantic models.
    """
    try:
        result = CalculationFactory.calculate(payload.a, payload.b, payload.type)
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Cannot divide by zero")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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