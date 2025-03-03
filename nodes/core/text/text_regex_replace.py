import re

from ...categories import TEXT_CAT


class TextRegexReplace:
    """Performs pattern-based text replacement using regular expressions.

    A powerful text processing node that uses regex patterns to find and replace text patterns,
    supporting complex pattern matching and replacement operations.

    Args:
        text (str): The input text to process. Required.
        pattern (str): The regular expression pattern to match. Required.
        replacement (str): The string to use as replacement for matched patterns. Required.

    Returns:
        tuple[str]: A single-element tuple containing the processed text.

    Notes:
        - Invalid regex patterns will cause errors
        - Empty pattern or replacement strings are allowed
        - Supports all Python regex syntax including groups and backreferences
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "pattern": ("STRING", {"default": ""}),
                "replacement": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = TEXT_CAT
    DESCRIPTION = "Performs pattern-based text replacement using regular expressions. Uses regex patterns to find and replace text patterns, supporting complex pattern matching and replacement operations."

    def execute(self, text: str, pattern: str = "", replacement: str = "") -> tuple[str]:
        return (re.sub(pattern, replacement, text),)
