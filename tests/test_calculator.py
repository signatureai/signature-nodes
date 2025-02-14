# tests/test_calculator.py

import pytest
from calculator import Calculator


def test_addition():
    calc = Calculator()
    assert calc.add(3, 5) == 8
    assert calc.add(-1, 1) == 0
    assert calc.add(0, 0) == 0


def test_subtraction():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2
    assert calc.subtract(1, 1) == 0
    assert calc.subtract(0, 5) == -5


def test_multiplication():
    calc = Calculator()
    assert calc.multiply(3, 5) == 15
    assert calc.multiply(-2, 3) == -6
    assert calc.multiply(0, 5) == 0


def test_division():
    calc = Calculator()
    assert calc.divide(6, 2) == 3
    assert calc.divide(5, 2) == 2.5
    assert calc.divide(0, 5) == 0


def test_divide_by_zero():
    calc = Calculator()
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(5, 0)
