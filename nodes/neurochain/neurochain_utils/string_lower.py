from ...categories import NEUROCHAIN_UTILS_CAT


class StringLower:
    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "string": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "process"
    CATEGORY = NEUROCHAIN_UTILS_CAT
    OUTPUT_NODE = True

    def process(self, string: str):
        output = string.lower()
        return (output,)
