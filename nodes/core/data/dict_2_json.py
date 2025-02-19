import json

from ...categories import DATA_CAT


class Dict2Json:
    """Converts Python dictionaries to JSON strings for data interchange.

    A node that serializes Python dictionaries into JSON-formatted strings, facilitating data
    export and communication with external systems that require JSON format.

    Args:
        dict (dict): The Python dictionary to serialize.
            Can contain nested dictionaries, lists, and primitive Python types.
            All values must be JSON-serializable (dict, list, str, int, float, bool, None).

    Returns:
        tuple[str]: A single-element tuple containing:
            - str: The JSON-formatted string representation of the input dictionary.
                  Follows standard JSON syntax and escaping rules.

    Raises:
        TypeError: When dict contains values that cannot be serialized to JSON.
        ValueError: When dict is not a dictionary type.

    Notes:
        - All dictionary keys are converted to strings in the output JSON
        - Complex Python objects (datetime, custom classes) must be pre-converted to basic types
        - Output is compact JSON without extra whitespace or formatting
        - Handles nested structures of any depth
        - Unicode characters are properly escaped in the output
        - Circular references are not supported and will raise TypeError
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "dict": ("DICT",),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CLASS_ID = "dict_json"
    CATEGORY = DATA_CAT

    def execute(self, dict: dict) -> tuple[str]:
        json_str = json.dumps(dict)
        return (json_str,)
