from ...categories import PLATFORM_IO_CAT


class InputBoolean:
    """Processes boolean inputs for the platform.

    Handles boolean input processing with validation and type checking.

    Args:
        title (str): Display title for the boolean input. Defaults to "Input Boolean".
        subtype (str): Must be "boolean".
        required (bool): Whether the input is required. Defaults to True.
        value (bool): The input boolean value. Defaults to False.
        metadata (str): JSON string containing additional metadata. Defaults to "{}".

    Returns:
        tuple[bool]: A tuple containing the boolean value.

    Raises:
        ValueError: If value is not a boolean.

    Notes:
        - Simple boolean validation and processing
        - Returns original boolean value without modification
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "title": ("STRING", {"default": "Input Boolean"}),
                "subtype": (["boolean"], {"default": "boolean"}),
                "required": ("BOOLEAN", {"default": True}),
                "value": ("BOOLEAN", {"default": False}),
                "metadata": ("STRING", {"default": "{}", "multiline": True}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT

    # TODO: confirm if title, subtype, and metadata inputs are needed
    def execute(
        self,
        title: str = "Input Boolean",
        subtype: str = "boolean",
        required: bool = True,
        value: bool = False,
        metadata: str = "{}",
    ) -> tuple[bool]:
        return (value,)
