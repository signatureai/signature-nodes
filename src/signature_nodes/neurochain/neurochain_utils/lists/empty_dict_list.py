from ....categories import LISTS_CAT


class EmptyDictList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "num_entries": ("INT", {"default": 5}),
            },
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("list",)
    FUNCTION = "process"
    CATEGORY = LISTS_CAT
    OUTPUT_NODE = True

    def process(self, num_entries: int):
        dict_list = [{} for _ in range(num_entries)]
        return (dict_list,)
