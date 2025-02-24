from .... import MAX_FLOAT
from ...categories import NUMBERS_CAT
from .shared import BASIC_OPERATORS


class FloatOperator:
    """Performs arithmetic operations on two floating-point numbers.

    This class supports basic arithmetic operations between two floating-point numbers. The supported
    operations are addition, subtraction, multiplication, and division.

    Args:
        left (float): The left operand for the arithmetic operation.
        right (float): The right operand for the arithmetic operation.
        operator (str): The arithmetic operator to use ('+', '-', '*', or '/').

    Returns:
        tuple[float]: A single-element tuple containing the result of the operation.

    Raises:
        ValueError: If either operand is not a float or if the operator is not supported.

    Notes:
        - Division by zero will raise a Python exception
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
        - Input values are limited by MAX_FLOAT constant
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "left": (
                    "FLOAT",
                    {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                ),
                "right": (
                    "FLOAT",
                    {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                ),
                "operator": (["+", "-", "*", "/", "%"],),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    DEPRECATED = True

    def execute(self, left: float = 0.0, right: float = 0.0, operator: str = "+") -> tuple[float]:
        if operator in BASIC_OPERATORS:
            return (BASIC_OPERATORS[operator](left, right),)

        raise ValueError(f"Unsupported operator: {operator}")
