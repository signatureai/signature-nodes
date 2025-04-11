from ...categories import NEUROCHAIN_UTILS_CAT


class LinesToStringList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lines": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("LIST",)
    FUNCTION = "process"
    CATEGORY = NEUROCHAIN_UTILS_CAT
    OUTPUT_NODE = True

    def process(self, lines: str):
        return ([line for line in lines.split("\n") if line.strip()],)
