from .... import MAX_FLOAT
from ...categories import NUMBERS_CAT


class FloatClamp:
    """Clamps a floating-point value between specified minimum and maximum bounds.

    This class provides functionality to constrain a float input within a defined range. If the input
    number is less than the minimum value, it returns the minimum value. If it's greater than the
    maximum value, it returns the maximum value.

    Args:
        number (float): The input float to be clamped.
        min_value (float): The minimum allowed value.
        max_value (float): The maximum allowed value.

    Returns:
        tuple[float]: A single-element tuple containing the clamped float value.

    Raises:
        ValueError: If any of the inputs (number, min_value, max_value) are not floats.

    Notes:
        - The input range is limited by MAX_FLOAT constant
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "number": (
                    "FLOAT",
                    {
                        "default": 0,
                        "forceInput": True,
                        "min": -MAX_FLOAT,
                        "max": MAX_FLOAT,
                    },
                ),
                "max_value": (
                    "FLOAT",
                    {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                ),
                "min_value": (
                    "FLOAT",
                    {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT

    def execute(self, number: float = 0.0, max_value: float = 0.0, min_value: float = 0.0) -> tuple[float]:
        if max_value < min_value:
            raise ValueError("Max value must be greater than or equal to min value")
        if number < min_value:
            return (min_value,)
        if number > max_value:
            return (max_value,)
        return (number,)
