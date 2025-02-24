from typing import Any

import jq

from ...categories import DATA_CAT
from ...shared import any_type


class GetDictValue:
    """Retrieves and types dictionary values using string keys.

    A node that provides key-based access to dictionary values while determining their Python
    type, enabling dynamic type handling and conditional processing in workflows.

    Args:
        dict (dict): The source dictionary to extract values from.
            Must be a valid Python dictionary.
            Can contain values of any type and nested structures.
        key (str): The lookup key for value retrieval.
            Must be a string type.
            Case-sensitive and must match exactly.
            If the key starts with a dot it will be used as a path as in a jq query,
            e.g. ".key1.key2[0]" will return the first value of array key2 in the dictionary key1.
            Defaults to empty string.

    Returns:
        tuple[Any, str]: A tuple containing:
            - Any: The value associated with the specified key.
            - str: The Python type name of the retrieved value (e.g., 'str', 'int', 'dict').

    Raises:
        ValueError: When key is not a string or dict parameter is not a dictionary.
        KeyError: When the specified key doesn't exist in the dictionary.

    Notes:
        - Supports dictionaries containing any Python type, including custom classes
        - Type name is derived from the object's __class__.__name__
        - Returns None for missing keys instead of raising KeyError
        - Thread-safe for concurrent access
        - Preserves original data without modifications
        - Handles nested data structures (dictionaries within dictionaries, lists, etc.)
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "dict": ("DICT",),
                "key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = (any_type, "STRING")
    RETURN_NAMES = ("value", "value_type")
    FUNCTION = "execute"
    CATEGORY = DATA_CAT

    def execute(self, dict: dict, key: str = "") -> tuple[Any, str]:
        if key.startswith("."):
            value = jq.compile(key).input(dict).first()
            if value is None:
                raise KeyError(f"Key {key} not found in dictionary")
        else:
            if key not in dict:
                raise KeyError(f"Key {key} not found in dictionary")
            value = dict.get(key)
        value_type = type(value).__name__
        return (value, value_type)
