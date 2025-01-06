from ....categories import ANY_CAT
from ...utils import WILDCARD


class AnyToDict:
    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "any_value": (WILDCARD, {}),
            }
        }

    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("dict_value",)
    FUNCTION = "process"
    CATEGORY = ANY_CAT
    OUTPUT_NODE = True

    def process(self, any_value):
        return (any_value,)
