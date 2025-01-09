from ....categories import LISTS_CAT


class DictListSet:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dict_list": ("LIST", {}),
                "key": ("STRING", {"default": ""}),
                "values": ("LIST", {"default": ""}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("dict_list",)
    FUNCTION = "process"
    CATEGORY = LISTS_CAT
    OUTPUT_NODE = True

    def process(self, dict_list: list, key: str, values: list):
        for idx, dict_obj in enumerate(dict_list):
            dict_obj[key] = values[idx]
        return (dict_list,)
