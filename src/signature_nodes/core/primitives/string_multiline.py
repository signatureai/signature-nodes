from ...categories import PRIMITIVES_CAT


class StringMultiline:
    """A node that handles multi-line string inputs.

    This node provides functionality for processing multi-line text input. It can be used as a
    basic input node in computational graphs where larger text blocks or formatted text
    processing is required.

    Args:
        value (str): The input multi-line string to process.
                    Default: "" (empty string)

    Returns:
        tuple[str]: A single-element tuple containing the processed multi-line string value.

    Notes:
        - The node maintains the exact input value without any transformation
        - Newline characters are preserved in the input
        - Suitable for longer text inputs, code blocks, or formatted text
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = PRIMITIVES_CAT
    DESCRIPTION = """
    A node that handles multi-line string inputs.
    Provides functionality for processing multi-line text input.
    Can be used as a basic input node in computational graphs where,
    larger text blocks or formatted text processing is required.
    """

    def execute(self, value: str = "") -> tuple[str]:
        return (value,)
