from ....categories import LISTS_CAT


class DictListGet:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dict_list": ("LIST", {}),
                "key": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("value_list",)
    FUNCTION = "process"
    CATEGORY = LISTS_CAT
    OUTPUT_NODE = True

    def process(self, dict_list: list, key: str):
        results = [None for _ in range(len(dict_list))]
        for idx, dict_obj in enumerate(dict_list):
            results[idx] = dict_obj[key]
        return (results,)
