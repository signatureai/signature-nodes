import json

from ....categories import LISTS_CAT


class JsonListToDictList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_list": ("LIST",),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("list",)
    FUNCTION = "process"
    CATEGORY = LISTS_CAT
    OUTPUT_NODE = True

    def process(self, json_list: list):
        dict_list = [None for _ in range(len(json_list))]

        for idx, json_str in enumerate(json_list):
            dict_list[idx] = json.loads(json_str)
        return (dict_list,)
