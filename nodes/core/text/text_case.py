from ...categories import TEXT_CAT


class TextCase:
    """Transforms text case according to specified formatting rules.

    A utility node that provides various case transformation options for input text, including
    lowercase, uppercase, capitalization, and title case conversion.

    Args:
        text (str): The input text to be transformed. Required.
        case (str): The case transformation to apply. Must be one of:
            - 'lower': Convert text to lowercase
            - 'upper': Convert text to uppercase
            - 'capitalize': Capitalize the first character
            - 'title': Convert text to title case

    Returns:
        tuple[str]: A single-element tuple containing the transformed text.

    Notes:
        - Empty input text will result in an empty string output
        - The transformation preserves any existing spacing and special characters
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "case": (["lower", "upper", "capitalize", "title"],),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = TEXT_CAT
    DESCRIPTION = """
    Transforms text case according to specified formatting rules.
    Provides various case transformation options for input text,
    including lowercase, uppercase, capitalization, and title case conversion.
    """

    def execute(self, text: str, case: str = "lower") -> tuple[str]:
        return (getattr(text, case)(),)
