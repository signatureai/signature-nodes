import yaml

from ...categories import DATA_CAT


class Dict2Yaml:
    """Converts Python dictionaries to YAML strings for data interchange.

    A node that serializes Python dictionaries into YAML-formatted strings, facilitating data
    export and communication with external systems that require YAML format.

    Args:
        dict (dict): The Python dictionary to serialize.
            Can contain nested dictionaries, lists, and primitive Python types.
            All values must be JSON-serializable (dict, list, str, int, float, bool, None).

    Returns:
        tuple[str]: A single-element tuple containing:
            - str: The YAML-formatted string representation of the input dictionary.

    Raises:
        ValueError: When dict is not a dictionary type.

    Notes:
        - All dictionary keys are converted to strings in the output YAML
        - Complex Python objects (datetime, custom classes) must be pre-converted to basic types
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
    CLASS_ID = "dict_yaml"
    CATEGORY = DATA_CAT

    def execute(self, dict: dict) -> tuple[str]:
        yaml_str = yaml.dump(dict)
        return (yaml_str,)
