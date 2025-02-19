import json
import os

from ...categories import FILE_CAT
from ...shared import BASE_COMFY_DIR


class FileLoader:
    """Processes string input into ComfyUI-compatible file data.

    Converts JSON-formatted string data into file references with proper paths for ComfyUI processing.
    Handles both single files and multiple files separated by '&&'.

    Args:
        value (str): JSON-formatted string containing file data.

    Returns:
        tuple[list]:
            - files: List of dictionaries with file data and updated paths

    Raises:
        ValueError: If input is not a string
        json.JSONDecodeError: If JSON parsing fails
        KeyError: If required file data fields are missing

    Notes:
        - Automatically prepends ComfyUI input folder path
        - Supports multiple files via '&&' separator
        - Preserves original file metadata
        - Updates file paths for ComfyUI compatibility
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
