from ...categories import NUMBERS_CAT
from .shared import OP_FUNCTIONS


class FloatMinMax:
    """Determines the minimum or maximum value between two floating-point numbers.

    This class compares two float inputs and returns either the smaller or larger value based on
    the specified mode of operation.

    Args:
        a (float): The first float to compare.
        b (float): The second float to compare.
        mode (str): The comparison mode ('min' or 'max').

    Returns:
        tuple[float]: A single-element tuple containing either the minimum or maximum value.

    Raises:
        ValueError: If either input is not a float or if the mode is not supported.

    Notes:
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "a": ("FLOAT", {"default": 0.0, "forceInput": True}),
                "b": ("FLOAT", {"default": 0.0, "forceInput": True}),
                "mode": (["min", "max"], {"default": "min"}),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    CLASS_ID = "float_minmax"
    DESCRIPTION = "Determines the minimum or maximum value between two floating-point numbers. Compares two float inputs and returns either the smaller or larger value based on the specified mode of operation."

    def execute(self, a: float = 0.0, b: float = 0.0, mode: str = "min") -> tuple[float]:
        if mode in OP_FUNCTIONS:
            return (OP_FUNCTIONS[mode](a, b),)
        raise ValueError(f"Unsupported mode: {mode}")
