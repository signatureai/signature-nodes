import json
import os

from ...categories import FILE_CAT
from ...shared import BASE_COMFY_DIR


class FolderLoader:
    """Processes folder paths into ComfyUI-compatible file data.

    Converts folder path information into properly formatted file references for ComfyUI processing.
    Supports both single and multiple folder paths.

    Args:
        value (str): JSON-formatted string containing folder path data.

    Returns:
        tuple[list]:
            - files: List of dictionaries with file data and updated paths

    Raises:
        ValueError: If input is not a string
        json.JSONDecodeError: If JSON parsing fails
        KeyError: If required folder data fields are missing

    Notes:
        - Automatically prepends ComfyUI input folder path
        - Supports multiple folders via '&&' separator
        - Maintains folder structure information
        - Updates all paths for ComfyUI compatibility
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("FILE",)
    FUNCTION = "execute"
    CATEGORY = FILE_CAT
    DESCRIPTION = "Converts folder path information into ComfyUI-compatible file references. Handles both single and multiple folders (separated by '&&'). Automatically prepends proper input folder paths while maintaining folder structure."

    def execute(self, value: str = "") -> tuple[list]:
        data = value.split("&&") if "&&" in value else [value]
        input_folder = os.path.join(BASE_COMFY_DIR, "input")
        for i, _ in enumerate(data):
            json_str = data[i]
            data[i] = json.loads(json_str)
            item = data[i]
            if isinstance(item, dict):
                name = item.get("name", None)
                if name is None:
                    continue
                item["name"] = os.path.join(input_folder, name)
                data[i] = item
        return (data,)
