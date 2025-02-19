from ...categories import NUMBERS_CAT


class Int2Float:
    """Converts an integer to a floating-point number.

    This class handles the conversion of integer values to floating-point numbers using Python's
    built-in float() function.

    Args:
        number (int): The integer to convert to a float.

    Returns:
        tuple[float]: A single-element tuple containing the converted float value.

    Raises:
        ValueError: If the input value is not an integer.

    Notes:
        - The conversion is exact as all integers can be represented precisely as floats
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "number": ("INT", {"default": 0, "forceInput": True}),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    CLASS_ID = "int2float"

    def execute(self, number: int = 0) -> tuple[float]:
        try:
            return (float(number),)
        except (TypeError, ValueError):
            raise ValueError("Number must be convertible to integer")
