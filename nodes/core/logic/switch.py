from typing import Any

from ...categories import LOGIC_CAT
from ...shared import any_type


class Switch:
    """Switches between two input values based on a boolean condition.

    A logic gate that selects between two inputs of any type based on a boolean condition. When the
    condition is True, it returns the 'true' value; otherwise, it returns the 'false' value. This node
    is useful for creating conditional workflows and dynamic value selection.

    Args:
        condition (bool): The boolean condition that determines which value to return.
            Defaults to False if not provided.
        on_true (Any): The value to return when the condition is True. Can be of any type.
        on_false (Any): The value to return when the condition is False. Can be of any type.

    Returns:
        tuple[Any]: A single-element tuple containing either the 'true' or 'false' value based on
            the condition.

    Notes:
        - The node accepts inputs of any type, making it versatile for different data types
        - Both 'on_true' and 'on_false' values must be provided
        - The condition is automatically cast to boolean, with None being treated as False
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "on_true": (any_type, {"lazy": True}),
                "on_false": (any_type, {"lazy": True}),
                "condition": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    FUNCTION = "execute"
    CATEGORY = LOGIC_CAT

    def check_lazy_status(self, condition: bool, on_true: Any = None, on_false: Any = None) -> Any:
        if condition and on_true is None:
            return ["on_true"]
        if not condition and on_false is None:
            return ["on_false"]
        return None

    def execute(self, on_true: Any, on_false: Any, condition: bool = True) -> tuple[Any]:
        return (on_true if condition else on_false,)
