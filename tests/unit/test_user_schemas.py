# tests/unit/test_calculation_schemas.py
import pytest
from pydantic import ValidationError
from app.schemas import CalculationCreate, OperationType

def test_schema_valid_addition():
    payload = CalculationCreate(a=10, b=5, type=OperationType.ADD)
    assert payload.a == 10
    assert payload.type == OperationType.ADD

def test_schema_valid_division():
    payload = CalculationCreate(a=10, b=2, type=OperationType.DIVIDE)
    assert payload.b == 2

def test_schema_invalid_operation_type():
    with pytest.raises(ValidationError):
        # "modulo" is not a valid enum member
        CalculationCreate(a=10, b=2, type="modulo")

def test_schema_divide_by_zero_validation():
    # Pydantic validator should catch this
    with pytest.raises(ValidationError) as excinfo:
        CalculationCreate(a=10, b=0, type=OperationType.DIVIDE)
    
    assert "Cannot divide by zero" in str(excinfo.value)

def test_schema_add_with_zero_b_is_valid():
    # Adding 0 is perfectly fine
    payload = CalculationCreate(a=10, b=0, type=OperationType.ADD)
    assert payload.b == 0