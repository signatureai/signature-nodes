from ...categories import PRIMITIVES_CAT


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
    DESCRIPTION = "A node that handles boolean inputs. Provides functionality for processing boolean (True/False) values. Can be used as a basic input node in computational graphs where conditional logic is required."

    def execute(self, value: bool = False) -> tuple[bool]:
        return (value,)
