from neurochain.llms.ollama_llm import OllamaLLM as Ollama

from ...categories import LLM_CAT


class OllamaLLM:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "host": ("STRING", {"default": "http://localhost:11434"}),
                "model_name": ("STRING", {"default": "llama3.2"}),
            },
            "optional": {
                "auto_manage_ollama": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("BaseLLM",)
    RETURN_NAMES = ("llm",)
    FUNCTION = "process"
    CATEGORY = LLM_CAT
    OUTPUT_NODE = True

    def process(self, host: str, model_name: str, auto_manage_ollama: bool):
        llm = Ollama(host=host, model_name=model_name, auto_manage_ollama=auto_manage_ollama)
        return (llm,)
