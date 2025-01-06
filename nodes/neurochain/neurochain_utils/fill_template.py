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
        output = template

        for key, value in data_dict.items():
            output = output.replace(f"[{key}]", value)

        return (output,)
