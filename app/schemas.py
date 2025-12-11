# app/schemas.py
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, constr, ConfigDict, field_validator, Field, model_validator

# --- Enums for strict typing ---
class OperationType(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    MODULUS = "modulus"
    EXPONENT = "exponent"

# --- User Schemas ---
class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6, max_length=72)


class UserUpdate(BaseModel):
    username: constr(min_length=3, max_length=50) | None = None
    email: EmailStr | None = None


class PasswordChange(BaseModel):
    current_password: constr(min_length=1)
    new_password: constr(min_length=6, max_length=72)

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Calculation Schemas ---
class CalculationCreate(BaseModel):
    a: float
    b: float
    type: OperationType

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        # Enum handles allowed values, but we can add extra logic if needed
        return v
    @model_validator(mode="after")
    def check_division_by_zero(self):
        """Instance-level validator run after model creation to perform
        cross-field checks (e.g., division by zero).
        """
        if self.type == OperationType.DIVIDE and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self

class CalculationRead(BaseModel):
    id: int
    a: float
    b: float
    type: OperationType
    result: float
    timestamp: datetime
    user_id: int | None = None

    model_config = ConfigDict(from_attributes=True)