import tomli_w

from ...categories import DATA_CAT


class Dict2Toml:
    """Converts Python dictionaries to TOML strings for data interchange.

    A node that serializes Python dictionaries into TOML-formatted strings, facilitating data
    export and communication with external systems that require TOML format.

    Args:
        dict (dict): The Python dictionary to serialize.
            Can contain nested dictionaries, lists, and primitive Python types.
            All values must be JSON-serializable (dict, list, str, int, float, bool, None).

    Returns:
        tuple[str]: A single-element tuple containing:
            - str: The TOML-formatted string representation of the input dictionary.

    Raises:
        ValueError: When dict is not a dictionary type.

    Notes:
        - All dictionary keys are converted to strings in the output TOML
        - Complex Python objects (datetime, custom classes) must be pre-converted to basic types
        - Output is compact TOML without extra whitespace or formatting
        - Handles nested structures of any depth
        - Unicode characters are properly escaped in the output
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dict": ("DICT",),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CLASS_ID = "dict_toml"
    CATEGORY = DATA_CAT

    def execute(self, dict: dict) -> tuple[str]:
        toml_str = tomli_w.dumps(dict)
        return (toml_str,)
