from ....categories import ANY_CAT
from ....shared import any_type


class AnyToList:
    """Converts any value to a list."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any_value": (any_type, {}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("list_value",)
    FUNCTION = "process"
    CATEGORY = ANY_CAT
    OUTPUT_NODE = True

    def process(self, any_value):
        return (any_value,)
