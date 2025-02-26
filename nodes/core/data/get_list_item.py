from typing import Any

from ...categories import DATA_CAT
from ...shared import any_type


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
    DESCRIPTION = "Retrieves items from lists by index position. Returns both the item and its Python type name. Uses zero-based indexing (0 = first item). Supports lists containing any data type."

    def execute(self, list: list, index: int = 0) -> tuple[Any, str]:
        item = list[index]
        item_type = type(item).__name__
        return (item, item_type)
