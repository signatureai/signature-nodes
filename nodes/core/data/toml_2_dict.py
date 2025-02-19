import tomllib

from ...categories import DATA_CAT


class Toml2Dict:
    """Converts TOML strings to Python dictionaries for workflow integration.

    A node that takes TOML-formatted strings and parses them into Python dictionaries, enabling
    seamless data integration within the workflow. Handles nested TOML structures and validates
    input format.

    Args:
        toml_str (str): The TOML-formatted input string to parse.
            Must be a valid TOML string conforming to standard TOML syntax.
            Can represent simple key-value pairs or complex nested structures.

    Returns:
        tuple[dict]: A single-element tuple containing:
            - dict: The parsed Python dictionary representing the TOML structure.
                   Preserves all nested objects, arrays, and primitive values.

    Raises:
        ValueError: When toml_str is not a string type.
        toml.TomlDecodeError: When the input string contains invalid TOML syntax.

    Notes:
        - Accepts any valid TOML format including hash tables, arrays, and primitive values
        - Empty TOML tables ('[table]') are valid inputs and return empty dictionaries
        - Preserves all TOML data types: hash tables, arrays, strings, numbers, booleans, null
        - Unicode characters are properly handled and preserved
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "toml_str": ("STRING", {"default": "", "forceInput": True}),
            },
        }

    RETURN_TYPES = ("DICT",)
    FUNCTION = "execute"
    CLASS_ID = "toml_dict"
    CATEGORY = DATA_CAT

    def execute(self, toml_str: str = "") -> tuple[dict]:
        toml_dict = tomllib.loads(toml_str)
        return (toml_dict,)
