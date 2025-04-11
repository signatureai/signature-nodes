from ....categories import LISTS_CAT


class DictListFilter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dict_list": ("LIST", {}),
                "key": ("STRING", {"default": ""}),
                "condition": ([">", ">=", "<", "<=", "==", "!="],),
                "value": ("FLOAT", {"default": 1}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("dict_list",)
    FUNCTION = "process"
    CATEGORY = LISTS_CAT
    OUTPUT_NODE = True

    def process(self, dict_list: list, key: str, condition: str, value: float):
        filtered_list = []
        for idx, dict_obj in enumerate(dict_list):
            if condition == ">" and dict_obj[key] > value:
                filtered_list.append(dict_obj)
            elif condition == ">=" and dict_obj[key] >= value:
                filtered_list.append(dict_obj)
            elif condition == "<" and dict_obj[key] < value:
                filtered_list.append(dict_obj)
            elif condition == "<=" and dict_obj[key] <= value:
                filtered_list.append(dict_obj)
            elif condition == "==" and dict_obj[key] == value:
                filtered_list.append(dict_obj)
            elif condition == "!=" and dict_obj[key] != value:
                filtered_list.append(dict_obj)
        return (filtered_list,)
