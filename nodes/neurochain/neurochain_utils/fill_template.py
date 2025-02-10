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

        def replace_key(template: str, data: dict, parent_path: str = "") -> str:
            for key, value in data.items():
                if isinstance(value, dict):
                    template = replace_key(template, value, parent_path + key + ".")
                else:
                    template = template.replace(f"[{parent_path}{key}]", str(value))
            return template

        output = replace_key(template, data_dict)

        return (output,)
