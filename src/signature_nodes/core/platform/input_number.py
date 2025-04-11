from ...categories import PLATFORM_IO_CAT
from ...shared import any_type


class InputNumber:
    """Processes numeric inputs with type conversion.

    Handles numeric input processing with support for both integer and float values, including
    automatic type conversion based on the specified subtype.

    Args:
        title (str): Display title for the number input. Defaults to "Input Number".
        subtype (str): Type of number - either "float" or "int".
        required (bool): Whether the input is required. Defaults to True.
        value (float): The input numeric value. Defaults to 0.
        metadata (str): JSON string containing additional metadata. Defaults to "{}".

    Returns:
        tuple[Union[int, float]]: A tuple containing the processed numeric value.

    Raises:
        ValueError: If value is not numeric or subtype is invalid.

    Notes:
        - Automatically converts between float and int based on subtype
        - Maintains numeric precision during conversion
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "title": ("STRING", {"default": "Input Number"}),
                "subtype": (["float", "int"],),
                "required": ("BOOLEAN", {"default": True}),
                "value": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": -18446744073709551615,
                        "max": 18446744073709551615,
                        "step": 0.1,
                    },
                ),
                "metadata": ("STRING", {"default": "{}", "multiline": True}),
            },
        }

    RETURN_TYPES = (any_type,)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT
    DESCRIPTION = """
    Processes numeric inputs with type conversion.
    Handles numeric input processing with support for both integer and float values,
    including automatic type conversion based on the specified subtype.
    """

    def execute(
        self,
        title: str = "Input Number",
        subtype: str = "float",
        required: bool = True,
        value: float = 0,
        metadata: str = "{}",
    ) -> tuple[float]:
        if subtype == "int":
            value = round(value)
        elif subtype == "float":
            value = float(value)
        return (value,)
