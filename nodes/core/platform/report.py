from ...categories import PLATFORM_IO_CAT
from ...shared import any_type


class Report:
    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": (any_type,),
                "report": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("value",)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT
    OUTPUT_NODE = True

    def execute(self, value, report):
        data = {"type": "string", "value": report}
        return {"ui": {"signature_report": [data]}, "result": (value,)}
