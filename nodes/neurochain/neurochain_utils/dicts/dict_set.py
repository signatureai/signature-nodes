from ....categories import DICTS_CAT
from ...utils import WILDCARD


class DictSet:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_dict": ("DICT", {}),
                "key": ("STRING", {"default": ""}),
                "value": (WILDCARD,),
            }
        }

    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("new_dict",)
    FUNCTION = "process"
    CATEGORY = DICTS_CAT
    OUTPUT_NODE = True

    def process(self, input_dict: dict, key: str, value):
        input_dict[key] = value
        return (input_dict,)
