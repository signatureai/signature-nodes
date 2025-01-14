# Primitives Nodes

## Float

A node that handles floating-point number inputs with configurable parameters.

This node provides functionality for processing floating-point numbers within a specified range
and step size. It can be used as a basic input node in computational graphs where decimal
number precision is required.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | value | `FLOAT` | 0 | max=18446744073709551615, step=0.01 |

### Returns

| Name | Type |
|------|------|
| float | `FLOAT` |


??? note "Source code"

    ```python
    class Float:
        """A node that handles floating-point number inputs with configurable parameters.

        This node provides functionality for processing floating-point numbers within a specified range
        and step size. It can be used as a basic input node in computational graphs where decimal
        number precision is required.

        Args:
            value (float): The input floating-point number to process.
                          Default: 0
                          Min: -18446744073709551615
                          Max: 18446744073709551615
                          Step: 0.01

        Returns:
            tuple[float]: A single-element tuple containing the processed float value.

        Notes:
            - The node maintains the exact input value without any transformation
            - The step value of 0.01 provides two decimal places of precision by default
            - The min/max values correspond to the 64-bit integer limits
        """

        @classmethod
        def INPUT_TYPES(cls):  # type: ignore
            return {
                "required": {
                    "value": (
                        "FLOAT",
                        {"default": 0, "min": -18446744073709551615, "max": 18446744073709551615, "step": 0.01},
                    ),
                },
            }

        RETURN_TYPES = ("FLOAT",)
        RETURN_NAMES = ("float",)
        FUNCTION = "execute"
        CATEGORY = PRIMITIVES_CAT

        def execute(self, value):
            return (value,)


    ```

## Int

A node that handles integer number inputs with configurable parameters.

This node provides functionality for processing integer numbers within a specified range
and step size. It can be used as a basic input node in computational graphs where whole
number values are required.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | value | `INT` | 0 | max=18446744073709551615, step=1 |

### Returns

| Name | Type |
|------|------|
| int | `INT` |


??? note "Source code"

    ```python
    class Int:
        """A node that handles integer number inputs with configurable parameters.

        This node provides functionality for processing integer numbers within a specified range
        and step size. It can be used as a basic input node in computational graphs where whole
        number values are required.

        Args:
            value (int): The input integer number to process.
                        Default: 0
                        Min: -18446744073709551615
                        Max: 18446744073709551615
                        Step: 1

        Returns:
            tuple[int]: A single-element tuple containing the processed integer value.

        Notes:
            - The node maintains the exact input value without any transformation
            - The step value of 1 ensures whole number increments
            - The min/max values correspond to the 64-bit integer limits
        """

        @classmethod
        def INPUT_TYPES(cls):  # type: ignore
            return {
                "required": {
                    "value": (
                        "INT",
                        {"default": 0, "min": -18446744073709551615, "max": 18446744073709551615, "step": 1},
                    ),
                },
            }

        RETURN_TYPES = ("INT",)
        RETURN_NAMES = ("int",)
        FUNCTION = "execute"
        CATEGORY = PRIMITIVES_CAT

        def execute(self, value):
            return (value,)


    ```

## String

A node that handles single-line string inputs.

This node provides functionality for processing single-line text input. It can be used as a
basic input node in computational graphs where text processing is required.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | value | `STRING` |  |  |

### Returns

| Name | Type |
|------|------|
| string | `STRING` |


??? note "Source code"

    ```python
    class String:
        """A node that handles single-line string inputs.

        This node provides functionality for processing single-line text input. It can be used as a
        basic input node in computational graphs where text processing is required.

        Args:
            value (str): The input string to process.
                        Default: "" (empty string)

        Returns:
            tuple[str]: A single-element tuple containing the processed string value.

        Notes:
            - The node maintains the exact input value without any transformation
            - Newline characters are not preserved in the input field
            - Suitable for short text inputs or commands
        """

        @classmethod
        def INPUT_TYPES(cls):  # type: ignore
            return {
                "required": {
                    "value": ("STRING", {"default": ""}),
                },
            }

        RETURN_TYPES = ("STRING",)
        RETURN_NAMES = ("string",)
        FUNCTION = "execute"
        CATEGORY = PRIMITIVES_CAT

        def execute(self, value):
            return (value,)


    class StringMultiline:
        """A node that handles multi-line string inputs.

        This node provides functionality for processing multi-line text input. It can be used as a
        basic input node in computational graphs where larger text blocks or formatted text
        processing is required.

        Args:
            value (str): The input multi-line string to process.
                        Default: "" (empty string)

        Returns:
            tuple[str]: A single-element tuple containing the processed multi-line string value.

        Notes:
            - The node maintains the exact input value without any transformation
            - Newline characters are preserved in the input
            - Suitable for longer text inputs, code blocks, or formatted text
        """

        @classmethod
        def INPUT_TYPES(cls):  # type: ignore
            return {
                "required": {
                    "value": ("STRING", {"default": "", "multiline": True}),
                },
            }

        RETURN_TYPES = ("STRING",)
        RETURN_NAMES = ("string",)
        FUNCTION = "execute"
        CATEGORY = PRIMITIVES_CAT

        def execute(self, value):
            return (value,)


    ```

## StringMultiline

A node that handles multi-line string inputs.

This node provides functionality for processing multi-line text input. It can be used as a
basic input node in computational graphs where larger text blocks or formatted text
processing is required.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | value | `STRING` |  | multiline=True |

### Returns

| Name | Type |
|------|------|
| string | `STRING` |


??? note "Source code"

    ```python
    class StringMultiline:
        """A node that handles multi-line string inputs.

        This node provides functionality for processing multi-line text input. It can be used as a
        basic input node in computational graphs where larger text blocks or formatted text
        processing is required.

        Args:
            value (str): The input multi-line string to process.
                        Default: "" (empty string)

        Returns:
            tuple[str]: A single-element tuple containing the processed multi-line string value.

        Notes:
            - The node maintains the exact input value without any transformation
            - Newline characters are preserved in the input
            - Suitable for longer text inputs, code blocks, or formatted text
        """

        @classmethod
        def INPUT_TYPES(cls):  # type: ignore
            return {
                "required": {
                    "value": ("STRING", {"default": "", "multiline": True}),
                },
            }

        RETURN_TYPES = ("STRING",)
        RETURN_NAMES = ("string",)
        FUNCTION = "execute"
        CATEGORY = PRIMITIVES_CAT

        def execute(self, value):
            return (value,)


    ```

## Boolean

A node that handles boolean inputs.

This node provides functionality for processing boolean (True/False) values. It can be used
as a basic input node in computational graphs where conditional logic is required.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | value | `BOOLEAN` | False |  |

### Returns

| Name | Type |
|------|------|
| boolean | `BOOLEAN` |


??? note "Source code"

    ```python
    class Boolean:
        """A node that handles boolean inputs.

        This node provides functionality for processing boolean (True/False) values. It can be used
        as a basic input node in computational graphs where conditional logic is required.

        Args:
            value (bool): The input boolean value to process.
                         Default: False

        Returns:
            tuple[bool]: A single-element tuple containing the processed boolean value.

        Notes:
            - The node maintains the exact input value without any transformation
            - Typically displayed as a checkbox in user interfaces
            - Useful for conditional branching in node graphs
        """

        @classmethod
        def INPUT_TYPES(cls):  # type: ignore
            return {
                "required": {
                    "value": ("BOOLEAN", {"default": False}),
                },
            }

        RETURN_TYPES = ("BOOLEAN",)
        RETURN_NAMES = ("boolean",)
        FUNCTION = "execute"
        CATEGORY = PRIMITIVES_CAT

        def execute(self, value):
            return (value,)

    ```
