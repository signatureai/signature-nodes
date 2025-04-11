from neurochain.llms.ml_platform_llm import MLPlatformLLM as MLPlatform

from ...categories import LLM_CAT


class MLPlatformLLM:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "endpoint_name": (
                    "STRING",
                    {"default": "Meta-Llama-3-8B-Instruct-stg"},
                ),
            }
        }

    RETURN_TYPES = ("BaseLLM",)
    RETURN_NAMES = ("llm",)
    FUNCTION = "process"
    CATEGORY = LLM_CAT
    OUTPUT_NODE = True

    def process(self, endpoint_name: str):
        llm = MLPlatform(endpoint_name=endpoint_name)
        return (llm,)
