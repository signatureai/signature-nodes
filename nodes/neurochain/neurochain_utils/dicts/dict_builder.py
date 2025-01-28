from ....categories import DICTS_CAT


class DictBuilder:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key_values": ("LIST",),
            }
        }

    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("dict",)
    FUNCTION = "process"
    CATEGORY = DICTS_CAT
    OUTPUT_NODE = True

    def process(self, key_values: list):
        output = {}
        for key, value in key_values:
            output[key] = value
        return (output,)
