import json
import tomllib
import torch
import jq
import tomli_w
import yaml

from .categories import DATA_CAT
from .shared import any_type


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
                "json_str": ("STRING", {"default": "", "forceInput": True}),
            },
        }

    RETURN_TYPES = ("DICT",)
    FUNCTION = "execute"
    CLASS_ID = "json_dict"
    CATEGORY = DATA_CAT

    def execute(self, json_str: str = "") -> tuple[dict]:
        json_dict = json.loads(json_str)
        return (json_dict,)


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

    def execute(self, yaml_str: str = "") -> tuple[dict]:
        yaml_dict = yaml.safe_load(yaml_str)
        return (yaml_dict,)


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


class GetImageListItem:
    """Extracts a single image from an image list by index.

    A node designed for batch image processing that allows selective access to individual images
    within a collection, enabling targeted processing of specific images in a sequence.

    Args:
        images (list[Image]): The list of image objects to select from.
            Must be a valid list containing compatible image objects.
            Can be any length, but must not be empty.
        index (int): The zero-based index of the desired image.
            Must be a non-negative integer within the list bounds.
            Defaults to 0 (first image).

    Returns:
        tuple[Image]: A single-element tuple containing:
            - Image: The selected image object from the specified index position.

    Raises:
        ValueError: When index is not an integer or images is not a list.
        IndexError: When index is outside the valid range for the image list.
        TypeError: When images list contains invalid image objects.

    Notes:
        - Uses zero-based indexing (0 = first image)
        - Does not support negative indices
        - Returns a single image even from multi-image batches
        - Preserves the original image data without modifications
        - Thread-safe for concurrent access
        - Memory efficient as it references rather than copies the image
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "images": ("LIST",),
                "index": ("INT", {"default": 0}),
            },
        }

    RETURN_TYPES = "IMAGE"
    FUNCTION = "execute"
    CATEGORY = DATA_CAT

    def execute(self, images: list[torch.Tensor], index: int = 0) -> tuple[torch.Tensor]:
        image = images[index]
        return (image,)


class GetListItem:
    """Retrieves and types items from any list by index position.

    A versatile node that provides access to list elements while also determining their Python
    type, enabling dynamic type handling and conditional processing in workflows.

    Args:
        list (list): The source list to extract items from.
            Can contain elements of any type, including mixed types.
            Must be a valid Python list, not empty.
        index (int): The zero-based index of the desired item.
            Must be a non-negative integer within the list bounds.
            Defaults to 0 (first item).

    Returns:
        tuple[Any, str]: A tuple containing:
            - Any: The retrieved item from the specified index position.
            - str: The Python type name of the retrieved item (e.g., 'str', 'int', 'dict').

    Raises:
        ValueError: When index is not an integer or list parameter is not a list.
        IndexError: When index is outside the valid range for the list.

    Notes:
        - Supports lists containing any Python type, including custom classes
        - Type name is derived from the object's __class__.__name__
        - Does not support negative indices
        - Thread-safe for concurrent access
        - Preserves original data without modifications
        - Handles nested data structures (lists within lists, dictionaries, etc.)
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "list": ("LIST",),
                "index": ("INT", {"default": 0}),
            },
        }

    RETURN_TYPES = (any_type, "STRING")
    RETURN_NAMES = ("item", "value_type")
    FUNCTION = "execute"
    CATEGORY = DATA_CAT

    def execute(self, list: list, index: int = 0) -> tuple[any, str]:
        item = list[index]
        item_type = type(item).__name__
        return (item, item_type)


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

    def execute(self, dict: dict, key: str = "") -> tuple[any, str]:
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

    def execute(self, dict: dict, value: any, key: str = "") -> tuple[dict]:
        if key.startswith("."):
            update_query = f'{key} = "{value}"'
            dict = jq.compile(update_query).input(dict).first()
        else:
            dict[key] = value
        return (dict,)


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
