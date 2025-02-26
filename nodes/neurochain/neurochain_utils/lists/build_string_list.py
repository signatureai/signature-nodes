from ....categories import LISTS_CAT


class BuildStringList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "Example String"}),
                "num_entries": ("INT", {"default": 5}),
            },
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("string_list",)
    FUNCTION = "process"
    CATEGORY = LISTS_CAT
    OUTPUT_NODE = True

    def process(self, text: str, num_entries: int):
        string_list = [text for _ in range(num_entries)]
        return (string_list,)
