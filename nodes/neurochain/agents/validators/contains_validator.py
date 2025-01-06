from ....categories import AGENT_RESPONSE_VALIDATORS_CAT


class ContainsValidator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "contains": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("FUNCTION",)
    RETURN_NAMES = ("validator",)
    FUNCTION = "process"
    CATEGORY = AGENT_RESPONSE_VALIDATORS_CAT
    OUTPUT_NODE = True

    def process(self, contains: str):
        def validator(text: str):
            return contains in text

        return (validator,)
