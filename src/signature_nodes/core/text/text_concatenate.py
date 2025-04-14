from ...categories import TEXT_CAT


class TextConcatenate:
    """Combines two text strings into a single string.

    A basic text manipulation node that joins two input strings together in sequence,
    without any separator between them.

    Args:
        text1 (str): The first text string to concatenate. Defaults to empty string.
        text2 (str): The second text string to concatenate. Defaults to empty string.

    Returns:
        tuple[str]: A single-element tuple containing the concatenated text.

    Notes:
        - No separator is added between the strings
        - Empty strings are handled safely
        - The result will be the direct combination of text1 followed by text2
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text1": ("STRING", {"default": ""}),
                "text2": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = TEXT_CAT
    DESCRIPTION = """
    Combines two text strings into a single string.
    Joins two input strings together in sequence, without any separator between them.
    """

    def execute(self, text1: str = "", text2: str = "") -> tuple[str]:
        return (text1 + text2,)
