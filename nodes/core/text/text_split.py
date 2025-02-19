from ...categories import TEXT_CAT


class TextSplit:
    """Splits text into a list of segments using a specified delimiter.

    A utility node that divides input text into multiple segments based on a delimiter,
    creating a list of substrings.

    Args:
        text (str): The input text to be split. Required.
        delimiter (str): The character or string to use as the splitting point. Defaults to space.

    Returns:
        tuple[list[str]]: A single-element tuple containing a list of split text segments.

    Notes:
        - Empty input text will result in a list with one empty string
        - If the delimiter is not found, the result will be a single-element list
        - Consecutive delimiters will result in empty strings in the output list
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "delimiter": ("STRING", {"default": " "}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = TEXT_CAT
    OUTPUT_IS_LIST = (True,)

    def execute(self, text: str, delimiter: str = " ") -> tuple[list[str]]:
        return (text.split(delimiter),)
