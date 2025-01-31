from .categories import PRIMITIVES_CAT


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
                    {
                        "default": 0,
                        "min": -18446744073709551615,
                        "max": 18446744073709551615,
                        "step": 0.01,
                    },
                ),
            },
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = PRIMITIVES_CAT

    def execute(self, value: float = 0) -> tuple[float]:
        return (value,)


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
                    {
                        "default": 0,
                        "min": -18446744073709551615,
                        "max": 18446744073709551615,
                        "step": 1,
                    },
                ),
            },
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = PRIMITIVES_CAT

    def execute(self, value: int = 0) -> tuple[int]:
        return (value,)


class JoinStringMulti:
    """
    Creates single string, or a list of strings, from
    multiple input strings.
    You can set how many inputs the node has,
    with the **inputcount** and clicking update.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "inputcount": ("INT", {"default": 2, "min": 2, "max": 1000, "step": 1}),
                "delimiter": ("STRING", {"default": " ", "multiline": False}),
                "return_list": ("BOOLEAN", {"default": False}),
                "string_1": ("STRING", {"default": "", "forceInput": True}),
                "string_2": ("STRING", {"default": "", "forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "combine"
    CATEGORY = "KJNodes"

    def combine(
        self,
        inputcount: int = 2,
        delimiter: str = " ",
        return_list: bool = False,
        **kwargs,
    ) -> tuple[str] | tuple[list[str]]:
        string = kwargs["string_1"]
        strings = [string]  # Initialize a list with the first string
        for c in range(1, inputcount):
            new_string = kwargs[f"string_{c + 1}"]
            if return_list:
                strings.append(new_string)  # Add new string to the list
            else:
                string = string + delimiter + new_string
        if return_list:
            return (strings,)  # Return the list of strings
        else:
            return (string,)  # Return the combined string


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
    FUNCTION = "execute"
    CATEGORY = PRIMITIVES_CAT

    def execute(self, value: str = "") -> tuple[str]:
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
    FUNCTION = "execute"
    CATEGORY = PRIMITIVES_CAT

    def execute(self, value: str = "") -> tuple[str]:
        return (value,)


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
    FUNCTION = "execute"
    CATEGORY = PRIMITIVES_CAT

    def execute(self, value: bool = False) -> tuple[bool]:
        return (value,)
