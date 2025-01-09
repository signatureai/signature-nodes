# Data Nodes

## Json2Dict

Converts JSON strings to Python dictionaries for workflow integration.

A node that takes JSON-formatted strings and parses them into Python dictionaries, enabling
seamless data integration within the workflow. Handles nested JSON structures and validates
input format.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | json_str | `STRING` |  | forceInput=True |

### Returns

| Name | Type |
|------|------|
| dict | `DICT` |


??? note "Source code in data.py"

    ```python
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
        def INPUT_TYPES(cls):  # type: ignore
            return {
                "required": {
                    "json_str": ("STRING", {"default": "", "forceInput": True}),
                },
            }

        RETURN_TYPES = ("DICT",)
        FUNCTION = "execute"
        CLASS_ID = "json_dict"
        CATEGORY = DATA_CAT

        def execute(self, **kwargs):
            json_str = kwargs.get("json_str")
            if not isinstance(json_str, str):
                raise ValueError("Json string must be a string")
            json_dict = json.loads(json_str)
            return (json_dict,)


    ```

## Dict2Json

Converts Python dictionaries to JSON strings for data interchange.

A node that serializes Python dictionaries into JSON-formatted strings, facilitating data
export and communication with external systems that require JSON format.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | dict | `DICT` |  |  |

### Returns

| Name | Type |
|------|------|
| string | `STRING` |


??? note "Source code in data.py"

    ```python
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

        def execute(self, **kwargs):
            json_dict = kwargs.get("dict")
            json_str = json.dumps(json_dict)
            return (json_str,)


    ```

## GetImageListItem

Extracts a single image from an image list by index.

A node designed for batch image processing that allows selective access to individual images
within a collection, enabling targeted processing of specific images in a sequence.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | images | `IMAGE` |  |  |
| required | index | `INT` | 0 |  |

### Returns

| Name | Type |
|------|------|
| i | `I` |
| m | `M` |
| a | `A` |
| g | `G` |
| e | `E` |


??? note "Source code in data.py"

    ```python
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
                    "images": ("IMAGE",),
                    "index": ("INT", {"default": 0}),
                },
            }

        RETURN_TYPES = "IMAGE"
        RETURN_NAMES = "image"
        FUNCTION = "execute"
        CATEGORY = DATA_CAT

        def execute(self, **kwargs):
            images = kwargs.get("images")
            index = kwargs.get("index")
            if not isinstance(index, int):
                raise ValueError("Index must be an integer")
            if not isinstance(images, list):
                raise ValueError("Images must be a list")
            images = images[index]
            index = kwargs.get("index")
            image = images[index]
            return (image,)


    ```

## GetListItem

Retrieves and types items from any list by index position.

A versatile node that provides access to list elements while also determining their Python
type, enabling dynamic type handling and conditional processing in workflows.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | list | `LIST` |  |  |
| required | index | `INT` | 0 |  |

??? note "Source code in data.py"

    ```python
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

        def execute(self, **kwargs):
            list_obj = kwargs.get("list")
            index = kwargs.get("index")
            if not isinstance(index, int):
                raise ValueError("Index must be an integer")
            if not isinstance(list_obj, list):
                raise ValueError("Input must be a list")
            item = list_obj[index]
            item_type = type(item).__name__
            return (item, item_type)


    ```

## GetDictValue

Retrieves and types dictionary values using string keys.

A node that provides key-based access to dictionary values while determining their Python
type, enabling dynamic type handling and conditional processing in workflows.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | dict | `DICT` |  |  |
| required | key | `STRING` |  |  |

??? note "Source code in data.py"

    ```python
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

        def execute(self, **kwargs):
            dict_obj = kwargs.get("dict")
            key = kwargs.get("key")
            if not isinstance(key, str):
                raise ValueError("Key must be a string")
            if not isinstance(dict_obj, dict):
                raise ValueError("Dict must be a dictionary")
            value = dict_obj.get(key)
            value_type = type(value).__name__
            return (value, value_type)

    ```
