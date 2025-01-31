import re

import torch

from .categories import TEXT_CAT
from .shared import any_type


class TextPreview:
    """Processes and generates a preview of text inputs, supporting both strings and tensors.

    This node takes a list of text inputs and generates a formatted preview string. For tensor inputs,
    it includes shape information in the preview. The node is designed to handle multiple input types
    and provide a consistent preview format.

    Args:
        text (Any): A list of text inputs that can be strings, tensors, or other objects that can be
            converted to strings.

    Returns:
        dict: A dictionary containing:
            - ui (dict): UI-specific data with the preview text under the 'text' key
            - result (tuple): A tuple containing the generated preview string

    Notes:
        - Tensor inputs are displayed with their shape information
        - Multiple inputs are separated by newlines
        - None values are skipped in the preview generation
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": (any_type,),
            },
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ()
    FUNCTION = "execute"
    OUTPUT_NODE = True

    CATEGORY = TEXT_CAT

    def execute(self, value: any = []) -> tuple[dict]:
        text_string = ""
        for t in value:
            if t is None:
                continue
            if text_string != "":
                text_string += "\n"
            text_string += str(t.shape) if isinstance(t, torch.Tensor) else str(t)
        return {"ui": {"text": [text_string]}}


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

    def execute(self, text: str, case: str = "lower") -> tuple[str]:
        return (getattr(text, case)(),)


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

    def execute(self, text: str, trim_type: str = "both") -> tuple[str]:
        trim_types = {
            "both": text.strip,
            "left": text.lstrip,
            "right": text.rstrip,
        }
        return (trim_types[trim_type](),)


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

    def execute(self, text: str, pattern: str = "", replacement: str = "") -> tuple[str]:
        return (re.sub(pattern, replacement, text),)


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

    def execute(self, text: str = "", find: str = "", replace: str = "") -> tuple[str]:
        return (text.replace(find, replace),)


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

    def execute(self, text1: str = "", text2: str = "") -> tuple[str]:
        return (text1 + text2,)


# class RenderText:
#     """Renders text onto an existing image at specified coordinates.

#     Overlays text on an input image using a specified font and position,
#     returning the modified image with the rendered text.

#     Args:
#         image (torch.Tensor): The input image to overlay text on
#         text (str): The text to render
#         x (int): X coordinate for text placement
#         y (int): Y coordinate for text placement
#         font_path (str): Path to the font file (.ttf, .otf)
#         font_size (int): Size of the font in pixels
#         color (str): Color of the text in hex format (e.g. "#FFFFFF")

#     Returns:
#         torch.Tensor - Modified image tensor with text overlay
#     """

#     @classmethod
#     def INPUT_TYPES(cls):
#         return {
#             "required": {
#                 "image": ("IMAGE",),
#                 "text": ("STRING", {"default": "Text"}),
#                 "x": ("INT", {"default": 100, "min": 0}),
#                 "y": ("INT", {"default": 100, "min": 0}),
#                 "font_path": ("STRING", {"default": ""}),
#                 "font_size": ("INT", {"default": 300, "min": 1, "max": 1000}),
#                 "color": ("STRING", {"default": "#FFFFFF"}),
#             }
#         }

#     RETURN_TYPES = "IMAGE"
#     FUNCTION = "execute"
#     CATEGORY = TEXT_CAT

#     # * Fred please use the TensorImage class to manage the image
#     def execute(self, **kwargs):
#         image = kwargs.get("image")
#         text = kwargs.get("text")
#         x = kwargs.get("x")
#         y = kwargs.get("y")
#         font_path = kwargs.get("font_path")
#         font_size = kwargs.get("font_size")
#         color = kwargs.get("color")
#         input_image = Image.fromarray((image[0].cpu().numpy() * 255).astype(np.uint8))  # type: ignore

#         if input_image.mode != "RGBA":
#             input_image = input_image.convert("RGBA")

#         # Load font
#         try:
#             font = ImageFont.truetype(font_path, font_size)
#         except (OSError, ImportError):
#             font = ImageFont.load_default(size=font_size)

#         draw = ImageDraw.Draw(input_image)
#         draw.text((x, y), text, font=font, fill=color)
#         img_tensor = torch.from_numpy(np.array(input_image).astype(np.float32) / 255.0)

#         if len(img_tensor.shape) == 3:
#             img_tensor = img_tensor.unsqueeze(0)

#         return (img_tensor,)
