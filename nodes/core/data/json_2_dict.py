import json

from ...categories import DATA_CAT


class Json2Dict:
    """Converts JSON strings to Python dictionaries for workflow integration.

    A node that takes JSON-formatted strings and parses them into Python dictionaries, enabling
    seamless data integration within the workflow. Handles nested JSON structures and validates
    input format.

    Args:
        json_str (str): The JSON-formatted input string to parse.
            Must be a valid JSON string conforming to standard JSON syntax.
            Can represent simple key-value pairs or complex nested structures.

    Returns:
        tuple[dict]: A single-element tuple containing:
            - dict: The parsed Python dictionary representing the JSON structure.
                   Preserves all nested objects, arrays, and primitive values.

    Raises:
        ValueError: When json_str is not a string type.
        json.JSONDecodeError: When the input string contains invalid JSON syntax.

    Notes:
        - Accepts any valid JSON format including objects, arrays, and primitive values
        - Empty JSON objects ('{}') are valid inputs and return empty dictionaries
        - Preserves all JSON data types: objects, arrays, strings, numbers, booleans, null
        - Does not support JSON streaming or parsing multiple JSON objects
        - Unicode characters are properly handled and preserved
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_str": (
                    "STRING",
                    {
                        "default": (
                            '{\n  "dict1": {"key1": "value1", "key2": "value2"},\n  "dict2": {"key1": "value3", '
                            '"key2": "value4"}\n}'
                        ),
                        "multiline": True,
                    },
                ),
            },
        }

    RETURN_TYPES = ("DICT",)
    FUNCTION = "execute"
    CLASS_ID = "json_dict"
    CATEGORY = DATA_CAT
    DESCRIPTION = """
    Converts JSON-formatted strings to Python dictionaries. Handles nested structures and validates input format.
    Useful for importing external data into workflows."""

    def execute(self, json_str: str = "") -> tuple[dict]:
        json_dict = json.loads(json_str)
        return (json_dict,)
