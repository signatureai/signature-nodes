from ...categories import NEUROCHAIN_UTILS_CAT


class SplitText:
    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "token": ("STRING", {"default": "\n"}),
                "text": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("substrings",)
    FUNCTION = "process"
    CATEGORY = NEUROCHAIN_UTILS_CAT
    OUTPUT_NODE = True

    def process(self, token: str, text: str):
        if token == "\\n":
            output = text.split("\n")
        else:
            output = text.split(token)
        print(output)
        return (output,)
