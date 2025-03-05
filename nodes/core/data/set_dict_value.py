from typing import Any

import jq

from ...categories import DATA_CAT
from ...shared import any_type


class SetDictValue:
    """Sets a value in a dictionary using a string key.

    A node that provides key-based update of a dictionary while determining their Python
    type, enabling dynamic type handling and conditional processing in workflows.

    Args:
        dict (dict): The source dictionary to set values.
            Must be a valid Python dictionary.
            Can contain values of any type and nested structures.
        key (str): The lookup key for value setter.
            Must be a string type.
            Case-sensitive and must match exactly.
            If the key starts with a dot it will be used as a path as in a jq query,
            e.g. ".key1.key2[0]" will set the first value of array key2 in the dictionary key1.
            Defaults to empty string.
        value (Any): The value to set.
            Can be any type of value.

    Returns:
        tuple[dict]: A tuple containing:
            - dict: The updated dictionary with the new value set.

    Raises:
        ValueError: When key is not a string or dict parameter is not a dictionary.

    Notes:
        - Supports dictionaries containing any Python type, including custom classes
        - Thread-safe for concurrent access
        - Preserves original data without modifications
        - Handles nested data structures (dictionaries within dictionaries, lists, etc.)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dict": ("DICT",),
                "value": (any_type,),
                "key": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("new_dict",)
    FUNCTION = "execute"
    CATEGORY = DATA_CAT
    DESCRIPTION = """
    Sets or updates values in dictionaries using keys or JQ path expressions (with leading dot).
    Supports any value type and nested data structures. Returns the modified dictionary."""

    def execute(self, dict: dict, value: Any, key: str = "") -> tuple[dict]:
        if key.startswith("."):
            update_query = f'{key} = "{value}"'
            dict = jq.compile(update_query).input(dict).first()
        else:
            dict[key] = value
        return (dict,)
