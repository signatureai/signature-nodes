from ...categories import NEUROCHAIN_UTILS_CAT


class CutText:
    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "start_token": ("STRING", {"default": ""}),
                "end_token": ("STRING", {"default": ""}),
                "text": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "process"
    CATEGORY = NEUROCHAIN_UTILS_CAT
    OUTPUT_NODE = True

    def process(self, text: str, start_token: str, end_token: str):
        output = text

        start_token_pos = output.find(start_token)
        if start_token_pos != -1:
            output = output[start_token_pos + 1 :]

        end_token_pos = output.rfind(end_token)
        if end_token_pos != -1:
            output = output[:end_token_pos]

        return (output,)
