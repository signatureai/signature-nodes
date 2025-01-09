from neurochain.llms.ollama_llm import OllamaLLM as Ollama

from ...categories import LLM_CAT


class OllamaLLM:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "host": ("STRING", {"default": "http://54.75.240.180:11434"}),
                "model_name": ("STRING", {"default": "llama3:instruct"}),
            }
        }

    RETURN_TYPES = ("BaseLLM",)
    RETURN_NAMES = ("llm",)
    FUNCTION = "process"
    CATEGORY = LLM_CAT
    OUTPUT_NODE = True

    def process(self, host: str, model_name: str):
        llm = Ollama(host=host, model_name=model_name)
        return (llm,)
