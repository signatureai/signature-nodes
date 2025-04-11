from ...categories import TEXT_CAT


class TextTrim:
    """Removes whitespace from text according to specified trimming rules.

    A utility node that trims whitespace from text input, offering options to remove whitespace
    from the beginning, end, or both sides of the text.

    Args:
        text (str): The input text to be trimmed. Required.
        trim_type (str): The type of trimming to apply. Must be one of:
            - 'both': Trim whitespace from both ends
            - 'left': Trim whitespace from the start
            - 'right': Trim whitespace from the end

    Returns:
        tuple[str]: A single-element tuple containing the trimmed text.

    Notes:
        - Whitespace includes spaces, tabs, and newlines
        - Empty input text will result in an empty string output
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "trim_type": (["both", "left", "right"],),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = TEXT_CAT
    DESCRIPTION = """
    Removes whitespace from text according to specified trimming rules.
    Trims whitespace from text input, offering options to remove whitespace from the beginning,
    end, or both sides of the text.
    """

    def execute(self, text: str, trim_type: str = "both") -> tuple[str]:
        trim_types = {
            "both": text.strip,
            "left": text.lstrip,
            "right": text.rstrip,
        }
        return (trim_types[trim_type](),)
