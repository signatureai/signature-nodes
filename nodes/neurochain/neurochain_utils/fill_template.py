from neurochain.utils.utils import replace_key

from ...categories import NEUROCHAIN_UTILS_CAT


class FillTemplate:
    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "data_dict": ("DICT", {}),
                "template": ("STRING", {"multiline": True, "default": "Use [keyword] to fill template"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "process"
    CATEGORY = NEUROCHAIN_UTILS_CAT
    OUTPUT_NODE = True

    def process(self, data_dict: dict, template: str):
        output = replace_key(template, data_dict)

        return (output,)
