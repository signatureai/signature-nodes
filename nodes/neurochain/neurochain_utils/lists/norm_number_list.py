from ....categories import LISTS_CAT


class NormNumberList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "num_list": ("LIST", {}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("norm_list",)
    FUNCTION = "process"
    CATEGORY = LISTS_CAT
    OUTPUT_NODE = True

    def process(self, num_list: list):
        norm_list = [None for _ in range(len(num_list))]

        max_num = max(num_list)

        for idx, x in enumerate(num_list):
            norm_list[idx] = x / max_num

        return (norm_list,)
