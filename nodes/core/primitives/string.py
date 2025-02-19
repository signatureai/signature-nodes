from ...categories import PRIMITIVES_CAT


class String:
    """A node that handles single-line string inputs.

    This node provides functionality for processing single-line text input. It can be used as a
    basic input node in computational graphs where text processing is required.

    Args:
        value (str): The input string to process.
                    Default: "" (empty string)

    Returns:
        tuple[str]: A single-element tuple containing the processed string value.

    Notes:
        - The node maintains the exact input value without any transformation
        - Newline characters are not preserved in the input field
        - Suitable for short text inputs or commands
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = PRIMITIVES_CAT

    def execute(self, value: str = "") -> tuple[str]:
        return (value,)
