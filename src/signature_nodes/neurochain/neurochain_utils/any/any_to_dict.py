from ....categories import ANY_CAT
from ....shared import any_type


class AnyToDict:
    """Converts any value to a dictionary."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any_value": (any_type, {}),
            }
        }

    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("dict_value",)
    FUNCTION = "process"
    CATEGORY = ANY_CAT
    OUTPUT_NODE = True

    def process(self, any_value):
        return (any_value,)
