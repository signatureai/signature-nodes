from ...categories import NUMBERS_CAT


class Float2Int:
    """Converts a floating-point number to an integer through truncation.

    This class handles the conversion of float values to integers by removing the decimal portion.
    The conversion is performed using Python's built-in int() function, which truncates towards zero.

    Args:
        number (float): The floating-point number to convert to an integer.

    Returns:
        tuple[int]: A single-element tuple containing the converted integer value.

    Raises:
        ValueError: If the input value is not a float.

    Notes:
        - Decimal portions are truncated, not rounded
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "number": ("FLOAT", {"default": 0, "forceInput": True}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    CLASS_ID = "float2int"
    DESCRIPTION = """
    Converts a floating-point number to an integer through truncation.
    Removes the decimal portion of a float value, truncating towards zero rather than rounding.
    Useful for workflows requiring integer values.
    """

    def execute(self, number: float = 0.0) -> tuple[int]:
        try:
            return (int(number),)
        except (TypeError, ValueError):
            raise ValueError("Number must be convertible to float")
