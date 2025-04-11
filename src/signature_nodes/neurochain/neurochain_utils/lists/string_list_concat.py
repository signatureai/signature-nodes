from ....categories import LISTS_CAT


class StringListConcat:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_list": ("LIST", {}),
                "sep": ("STRING", {"default": "\n"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "process"
    CATEGORY = LISTS_CAT
    OUTPUT_NODE = True

    def process(self, string_list: list, sep: str):
        sep = "\n" if sep == "\\n" else sep
        output = sep.join(string_list)
        return (output,)
