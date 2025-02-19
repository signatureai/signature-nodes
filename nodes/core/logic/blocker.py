from typing import Any

from comfy_execution.graph import ExecutionBlocker  # type: ignore

from ...categories import LABS_CAT
from ...shared import any_type


class Blocker:
    """Controls flow execution based on a boolean condition.

    A utility node that blocks or allows execution flow based on a boolean flag. When the continue
    flag is False, it blocks execution by returning an ExecutionBlocker. When True, it passes through
    the input value unchanged.

    Args:
        continue (bool): Flag to control execution flow. When False, blocks execution.
        in (Any): The input value to pass through when execution is allowed.

    Returns:
        tuple[Any]: A single-element tuple containing either:
            - The input value if continue is True
            - An ExecutionBlocker if continue is False

    Notes:
        - Useful for conditional workflow execution
        - Can be used to create branches in execution flow
        - The ExecutionBlocker prevents downstream nodes from executing
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "should_continue": ("BOOLEAN", {"default": False}),
                "input": (any_type, {"default": None}),
            },
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("out",)
    CATEGORY = LABS_CAT
    FUNCTION = "execute"

    def execute(self, should_continue: bool = False, input: Any = None) -> tuple[Any]:
        return (input if should_continue else ExecutionBlocker(None),)
