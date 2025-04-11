from ....categories import LISTS_CAT


class ListLength:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any_list": ("LIST", {}),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("length",)
    FUNCTION = "process"
    CATEGORY = LISTS_CAT
    OUTPUT_NODE = True

    def process(self, any_list: list):
        output = len(any_list)
        return (output,)
