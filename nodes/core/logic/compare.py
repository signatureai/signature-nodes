from typing import Any

import torch

from ...categories import LOGIC_CAT
from ...shared import any_type


class Compare:
    """Compares two input values based on a specified comparison operation.

    A logic gate that evaluates a comparison between two inputs of any type. The comparison is determined
    by the specified operation, which can include equality, inequality, and relational comparisons. This
    node is useful for implementing conditional logic based on the relationship between two values.

    Args:
        a (Any): The first value to compare. Can be of any type.
        b (Any): The second value to compare. Can be of any type.
        comparison (str): The comparison operation to perform. Defaults to "a == b".
            Available options include:
            - "a == b": Checks if a is equal to b.
            - "a != b": Checks if a is not equal to b.
            - "a < b": Checks if a is less than b.
            - "a > b": Checks if a is greater than b.
            - "a <= b": Checks if a is less than or equal to b.
            - "a >= b": Checks if a is greater than or equal to b.

    Returns:
        tuple[bool]: A single-element tuple containing the result of the comparison as a boolean value.

    Notes:
        - The node accepts inputs of any type, making it versatile for different data types.
        - If the inputs are tensors, lists, or tuples,
          the comparison will be evaluated based on their shapes or lengths.
        - The output will be cast to a boolean value.
    """

    COMPARE_FUNCTIONS = {
        "a == b": lambda a, b: a == b,
        "a != b": lambda a, b: a != b,
        "a < b": lambda a, b: a < b,
        "a > b": lambda a, b: a > b,
        "a <= b": lambda a, b: a <= b,
        "a >= b": lambda a, b: a >= b,
    }

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        compare_functions = list(cls.COMPARE_FUNCTIONS.keys())
        return {
            "required": {
                "a": (any_type,),
                "b": (any_type,),
                "comparison": (compare_functions, {"default": "a == b"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("result",)
    FUNCTION = "execute"
    CATEGORY = LOGIC_CAT
    DESCRIPTION = "Compares two input values based on a specified comparison operation. Evaluates equality, inequality, and relational comparisons between inputs of any type. Handles special cases for tensors, lists, and tuples."

    def execute(self, a: Any, b: Any, comparison: str = "a == b") -> tuple[bool]:
        try:
            output = self.COMPARE_FUNCTIONS[comparison](a, b)
        except Exception as e:
            if isinstance(a, torch.Tensor) and isinstance(b, torch.Tensor):
                output = self.COMPARE_FUNCTIONS[comparison](a.shape, b.shape)
            elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
                output = self.COMPARE_FUNCTIONS[comparison](len(a), len(b))
            else:
                raise e

        if isinstance(output, torch.Tensor):
            output = output.all().item()
        elif isinstance(output, (list, tuple)):
            output = all(output)

        return (bool(output),)
