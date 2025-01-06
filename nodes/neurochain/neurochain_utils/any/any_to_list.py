from ....categories import ANY_CAT
from ...utils import WILDCARD


class AnyToList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any_value": (WILDCARD, {}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("list_value",)
    FUNCTION = "process"
    CATEGORY = ANY_CAT
    OUTPUT_NODE = True

    def process(self, any_value):
        return (any_value,)
