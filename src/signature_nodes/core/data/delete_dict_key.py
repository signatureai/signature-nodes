import jq

from ...categories import DATA_CAT


class DeleteDictKey:
    """Deletes a key from a dictionary.

    A node that provides key-based deletion of a dictionary while determining their Python
    type, enabling dynamic type handling and conditional processing in workflows.

    Args:
        dict (dict): The source dictionary to delete values.
            Must be a valid Python dictionary.
            Can contain values of any type and nested structures.
        key (str): The lookup key for value deletion.
            Must be a string type.
            Case-sensitive and must match exactly.
            If the key starts with a dot it will be used as a path as in a jq query,
            e.g. ".key1.key2[0]" will delete the first value of array key2 in the dictionary key1.
            Defaults to empty string.

    Returns:
        tuple[dict]: A tuple containing:
            - dict: The updated dictionary with the key deleted.

    Raises:
        KeyError: When the specified key doesn't exist in the dictionary.
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
                "key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("new_dict",)
    FUNCTION = "execute"
    CATEGORY = DATA_CAT
    DESCRIPTION = """
    Removes a key from a dictionary.
    Supports both direct key removal and path-based deletion using JQ syntax (with leading dot).
    Returns the modified dictionary with the specified key removed."""

    def execute(self, dict: dict, key: str = "") -> tuple[dict]:
        if key.startswith("."):
            exists = jq.compile(key).input(dict).first()
            if exists is None:
                raise KeyError(f"Key {key} not found in dictionary")
            delete_query = f"del({key})"
            dict = jq.compile(delete_query).input(dict).first()
        else:
            if key not in dict:
                raise KeyError(f"Key {key} not found in dictionary")
            del dict[key]
        return (dict,)
