from ....categories import DICTS_CAT


class EmptyDict:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("empty_dict",)
    FUNCTION = "process"
    CATEGORY = DICTS_CAT
    OUTPUT_NODE = True

    def process(self):
        return ({},)
