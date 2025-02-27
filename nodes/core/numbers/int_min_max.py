from ...categories import NUMBERS_CAT
from .shared import OP_FUNCTIONS


class IntMinMax:
    """Determines the minimum or maximum value between two integers.

    This class compares two integer inputs and returns either the smaller or larger value based on
    the specified mode of operation.

    Args:
        a (int): The first integer to compare.
        b (int): The second integer to compare.
        mode (str): The comparison mode ('min' or 'max').

    Returns:
        tuple[int]: A single-element tuple containing either the minimum or maximum value.

    Raises:
        ValueError: If either input is not an integer or if the mode is not supported.

    Notes:
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "a": ("INT", {"default": 0, "forceInput": True}),
                "b": ("INT", {"default": 0, "forceInput": True}),
                "mode": (["min", "max"], {"default": "min"}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    CLASS_ID = "int_minmax"
    DESCRIPTION = "Determines the minimum or maximum value between two integers. Compares two integer inputs and returns either the smaller or larger value based on the specified mode of operation."

    def execute(self, a: int = 0, b: int = 0, mode: str = "min") -> tuple[int]:
        if mode in OP_FUNCTIONS:
            return (OP_FUNCTIONS[mode](a, b),)
        raise ValueError(f"Unsupported mode: {mode}")
