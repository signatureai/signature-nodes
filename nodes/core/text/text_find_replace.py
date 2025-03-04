from ...categories import TEXT_CAT


class TextFindReplace:
    """Performs simple text replacement without regex support.

    A straightforward text processing node that replaces all occurrences of a substring with
    another substring, using exact matching.

    Args:
        text (str): The input text to process. Defaults to empty string.
        find (str): The substring to search for. Defaults to empty string.
        replace (str): The substring to replace matches with. Defaults to empty string.

    Returns:
        tuple[str]: A single-element tuple containing the processed text.

    Notes:
        - Case-sensitive matching
        - All occurrences of the 'find' string will be replaced
        - Empty strings for any parameter are handled safely
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "text": ("STRING", {"default": ""}),
                "find": ("STRING", {"default": ""}),
                "replace": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = TEXT_CAT
    DESCRIPTION = """
    Performs simple text replacement without regex support.
    Replaces all occurrences of a substring with another substring,
    using exact matching.
    """

    def execute(self, text: str = "", find: str = "", replace: str = "") -> tuple[str]:
        return (text.replace(find, replace),)
