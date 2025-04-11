import os
import sys

MAX_INT: int = sys.maxsize
MAX_FLOAT: float = sys.float_info.max
BASE_COMFY_DIR: str = os.path.dirname(os.path.realpath(__file__)).split("custom_nodes")[0]


class TautologyStr(str):
    """A string subclass that always returns False for inequality comparisons.

    This utility class is used for type checking in the node system, where certain type comparisons
    should always evaluate to equal regardless of the actual string content.

    Notes:
        - Overrides the __ne__ method to always return False
        - Inherits all other string functionality
        - Used primarily for internal type system implementation
    """


class ByPassTypeTuple(tuple):
    """A tuple subclass that modifies indexing behavior for type checking.

    This utility class wraps tuple items in TautologyStr when accessed by index, and limits index
    access to prevent out of bounds errors. Used for type system implementation in the node framework.

    Notes:
        - Limits index access to first element (index 0)
        - Wraps string items in TautologyStr
        - Preserves original values for non-string items
        - Used primarily for internal type system implementation
    """


class AnyType(str):
    """A string subclass representing a wildcard type that matches any other type.

    This utility class is used in the type system to represent a type that is compatible with all
    other types. It achieves this by always returning False for inequality comparisons.

    Notes:
        - Used to implement the '*' wildcard type in the node system
        - All type comparisons evaluate to equal
        - Used primarily for internal type system implementation
    """

    def __ne__(self, __value: object) -> bool:
        return False


any_type = AnyType("*")
