from ...categories import MATH_CAT


class ListAverage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"list": ("LIST",)},
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("average",)
    FUNCTION = "process"
    CATEGORY = MATH_CAT
    OUTPUT_NODE = True

    def process(self, list: list):
        if not all(isinstance(item, (int, float)) for item in list):
            raise ValueError("List contains non-numeric items")
        return (sum(list) / len(list),)
