from ...categories import NEUROCHAIN_UTILS_CAT


class ConcatenateText:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_0": ("STRING", {}),
                "string_1": ("STRING", {}),
            },
            "optional": {
                "string_2": ("STRING", {}),
                "string_3": ("STRING", {}),
                "string_4": ("STRING", {}),
                "string_5": ("STRING", {}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "process"
    CATEGORY = NEUROCHAIN_UTILS_CAT
    OUTPUT_NODE = True

    def process(
        self,
        string_0: str,
        string_1: str,
        string_2: str = "",
        string_3: str = "",
        string_4: str = "",
        string_5: str = "",
    ):

        output = string_0 + string_1 + string_2 + string_3 + string_4 + string_5

        return (output,)
