from .... import MAX_FLOAT
from ...categories import NUMBERS_CAT
from .shared import BASIC_OPERATORS


class IntOperator:
    """Performs arithmetic operations on two floats and returns an integer result.

    This class supports basic arithmetic operations between two floating-point numbers and returns
    the result as an integer. The supported operations are addition, subtraction, multiplication,
    and division.

    Args:
        left (float): The left operand for the arithmetic operation.
        right (float): The right operand for the arithmetic operation.
        operator (str): The arithmetic operator to use ('+', '-', '*', or '/').

    Returns:
        tuple[int]: A single-element tuple containing the result of the operation as an integer.

    Raises:
        ValueError: If either operand is not a float or if the operator is not supported.

    Notes:
        - Division results are converted to integers
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
                "operator": (["+", "-", "*", "/"],),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    DEPRECATED = True
    DESCRIPTION = """
    Performs arithmetic operations on two floats and returns an integer result.
    Supports addition, subtraction, multiplication, and division between two float values.
    Returns the calculated result as an integer.
    """

    def execute(self, left: float = 0.0, right: float = 0.0, operator: str = "+") -> tuple[int]:
        if operator in BASIC_OPERATORS:
            return (int(BASIC_OPERATORS[operator](left, right)),)

        raise ValueError(f"Unsupported operator: {operator}")
