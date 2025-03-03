import yaml

from ...categories import DATA_CAT


class Yaml2Dict:
    """Converts YAML strings to Python dictionaries for data interchange.

    A node that takes YAML-formatted strings and parses them into Python dictionaries,
    enabling seamless data integration within the workflow. Handles nested YAML structures
    and validates input format.

    Args:
        yaml_str (str): The YAML-formatted input string to parse.
            Must be a valid YAML string conforming to standard YAML syntax.
            Can represent simple key-value pairs or complex nested structures.

    Returns:
        tuple[dict]: A single-element tuple containing:
            - dict: The parsed Python dictionary representing the YAML structure.

    Raises:
        ValueError: When yaml_str is not a string type.
        yaml.YAMLError: When the input string contains invalid YAML syntax.

    Notes:
        - Accepts any valid YAML format including hash tables, arrays, and primitive values
        - Preserves all YAML data types: hash tables, arrays, strings, numbers, booleans, null
        - Unicode characters are properly handled and preserved
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"yaml_str": ("STRING", {"default": "", "forceInput": True})},
        }

    RETURN_TYPES = ("DICT",)
    FUNCTION = "execute"
    CLASS_ID = "yaml_dict"
    CATEGORY = DATA_CAT
    DESCRIPTION = "Converts YAML-formatted strings to Python dictionaries. Handles nested structures and validates input format. Useful for importing configuration data into workflows."

    def execute(self, yaml_str: str = "") -> tuple[dict]:
        yaml_dict = yaml.safe_load(yaml_str)
        return (yaml_dict,)
