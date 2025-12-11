import pytest
from app.operations import add, subtract, multiply, divide, modulus, exponent

def test_add():
    assert add(3, 5) == 8

def test_subtract():
    assert subtract(10, 4) == 6

def test_multiply():
    assert multiply(2, 5) == 10

def test_divide():
    assert divide(10, 2) == 5

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)


def test_modulus():
    assert modulus(10, 3) == 1


def test_modulus_by_zero():
    with pytest.raises(ZeroDivisionError):
        modulus(5, 0)


def test_exponent():
    assert exponent(2, 3) == 8
