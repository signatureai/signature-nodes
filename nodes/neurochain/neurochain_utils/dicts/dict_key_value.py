from ....categories import DICTS_CAT
from ...utils import WILDCARD


class DictKeyValue:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key": ("STRING", {"default": ""}),
                "value": (WILDCARD,),
            }
        }

    RETURN_TYPES = ("DictKeyValue",)
    RETURN_NAMES = ("dict_key_value",)
    FUNCTION = "process"
    CATEGORY = DICTS_CAT
    OUTPUT_NODE = True

    def process(self, key: str, value):
        output = (key, value)
        return (output,)
