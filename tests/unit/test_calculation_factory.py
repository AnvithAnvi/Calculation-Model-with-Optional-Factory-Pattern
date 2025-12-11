# tests/unit/test_calculation_factory.py
import pytest
from app.calculation_factory import CalculationFactory
from app.schemas import OperationType

def test_factory_add():
    result = CalculationFactory.calculate(10, 5, OperationType.ADD)
    assert result == 15

def test_factory_subtract():
    result = CalculationFactory.calculate(10, 3, OperationType.SUBTRACT)
    assert result == 7

def test_factory_multiply():
    result = CalculationFactory.calculate(3, 3, OperationType.MULTIPLY)
    assert result == 9

def test_factory_divide():
    result = CalculationFactory.calculate(10, 2, OperationType.DIVIDE)
    assert result == 5

def test_factory_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        CalculationFactory.calculate(10, 0, OperationType.DIVIDE)


def test_factory_modulus():
    result = CalculationFactory.calculate(10, 3, OperationType.MODULUS)
    assert result == 1


def test_factory_exponent():
    result = CalculationFactory.calculate(2, 5, OperationType.EXPONENT)
    assert result == 32