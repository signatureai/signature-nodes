from ...categories import PLATFORM_IO_CAT


class InputText:
    """Processes text input with fallback support.

    Handles text input processing with support for different subtypes and optional fallback values
    when input is empty.

    Args:
        title (str): Display title for the text input. Defaults to "Input Text".
        subtype (str): Type of text - "string", "positive_prompt", or "negative_prompt".
        required (bool): Whether the input is required. Defaults to True.
        value (str): The input text value.
        metadata (str): JSON string containing additional metadata. Defaults to "{}".
        fallback (str): Optional fallback text if input is empty.

    Returns:
        tuple[str]: A tuple containing the processed text value.

    Raises:
        ValueError: If value or fallback are not strings.

    Notes:
        - Empty inputs will use the fallback value if provided
        - Supports multiline text input
        - Special handling for prompt-type inputs
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "title": ("STRING", {"default": "Input Text"}),
                "subtype": (["string"],),
                "required": ("BOOLEAN", {"default": True}),
                "value": ("STRING", {"multiline": True, "default": ""}),
                "metadata": ("STRING", {"default": "{}", "multiline": True}),
            },
            "optional": {
                "fallback": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT

    # TODO: confirm if title, subtype required and metadata inputs are needed
    def execute(
        self,
        title: str = "Input Text",
        subtype: str = "string",
        required: bool = True,
        value: str = "",
        metadata: str = "{}",
        fallback: str = "",
    ) -> tuple[str]:
        if fallback and value == "":
            value = fallback
        return (value,)
