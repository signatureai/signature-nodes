from .... import MAX_INT
from ...categories import NUMBERS_CAT


class IntClamp:
    """Clamps an integer value between specified minimum and maximum bounds.

    This class provides functionality to constrain an integer input within a defined range. If the input
    number is less than the minimum value, it returns the minimum value. If it's greater than the
    maximum value, it returns the maximum value.

    Args:
        number (int): The input integer to be clamped.
        min_value (int): The minimum allowed value.
        max_value (int): The maximum allowed value.

    Returns:
        tuple[int]: A single-element tuple containing the clamped integer value.

    Raises:
        ValueError: If any of the inputs (number, min_value, max_value) are not integers.

    Notes:
        - The input range is limited by MAX_INT constant
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "number": (
                    "INT",
                    {
                        "default": 0,
                        "forceInput": True,
                        "min": -MAX_INT,
                        "max": MAX_INT,
                    },
                ),
                "max_value": (
                    "INT",
                    {"default": 0, "min": -MAX_INT, "max": MAX_INT, "step": 1},
                ),
                "min_value": (
                    "INT",
                    {"default": 0, "min": -MAX_INT, "max": MAX_INT, "step": 1},
                ),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    DESCRIPTION = "Clamps an integer value between specified minimum and maximum bounds. Constrains an integer input within a defined range, returning the min value if input is too low or max value if input is too high."

    def execute(self, number: int = 0, max_value: int = 0, min_value: int = 0) -> tuple[int]:
        if max_value < min_value:
            raise ValueError("Max value must be greater than or equal to min value")
        if number < min_value:
            return (min_value,)
        if number > max_value:
            return (max_value,)
        return (number,)
