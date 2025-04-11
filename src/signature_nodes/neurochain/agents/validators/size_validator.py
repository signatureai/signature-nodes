from ....categories import AGENT_RESPONSE_VALIDATORS_CAT


class SizeValidator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "max_size": ("INT", {"min": 1, "default": 150}),
            }
        }

    RETURN_TYPES = ("FUNCTION",)
    RETURN_NAMES = ("validator",)
    FUNCTION = "process"
    CATEGORY = AGENT_RESPONSE_VALIDATORS_CAT
    OUTPUT_NODE = True

    def process(self, max_size: int):
        def validator(text: str):
            return len(text) <= max_size

        return (validator,)
