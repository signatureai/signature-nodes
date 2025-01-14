# Any Nodes

## AnyToList

Converts any value to a list.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | any_value | `WILDCARD` |  |  |

### Returns

| Name | Type |
|------|------|
| list | `LIST` |


??? note "Source code"

    ```python
    class AnyToList:
        """Converts any value to a list."""

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "any_value": (WILDCARD, {}),
                }
            }

        RETURN_TYPES = ("LIST",)
        RETURN_NAMES = ("list_value",)
        FUNCTION = "process"
        CATEGORY = ANY_CAT
        OUTPUT_NODE = True

        def process(self, any_value):
            return (any_value,)
    ```

## AnyToDict

Converts any value to a dictionary.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | any_value | `WILDCARD` |  |  |

### Returns

| Name | Type |
|------|------|
| dict | `DICT` |


??? note "Source code"

    ```python
    class AnyToDict:
        """Converts any value to a dictionary."""

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "any_value": (WILDCARD, {}),
                }
            }

        RETURN_TYPES = ("DICT",)
        RETURN_NAMES = ("dict_value",)
        FUNCTION = "process"
        CATEGORY = ANY_CAT
        OUTPUT_NODE = True

        def process(self, any_value):
            return (any_value,)

    ```
