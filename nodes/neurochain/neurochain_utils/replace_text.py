from ...categories import NEUROCHAIN_UTILS_CAT


class ReplaceText:
    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "old": ("STRING", {"default": ""}),
                "new": ("STRING", {"default": ""}),
                "text": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "process"
    CATEGORY = NEUROCHAIN_UTILS_CAT
    OUTPUT_NODE = True

    def process(self, text: str, old: str, new: str):
        output = text.replace(old, new)
        return (output,)
