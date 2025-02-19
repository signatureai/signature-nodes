from typing import Any

import torch

from ...categories import TEXT_CAT
from ...shared import any_type


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

    def execute(self, value: Any = []) -> tuple[dict]:
        text_string = ""
        for t in value:
            if t is None:
                continue
            if text_string != "":
                text_string += "\n"
            text_string += str(t.shape) if isinstance(t, torch.Tensor) else str(t)
        return {"ui": {"text": [text_string]}}
