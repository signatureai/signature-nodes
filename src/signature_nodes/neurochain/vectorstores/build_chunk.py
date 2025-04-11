from neurochain.utils.utils import Chunk

from ...categories import VECTORSTORE_CAT


class BuildChunk:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "chunk_text": ("STRING", {"default": ""}),
                "metadata": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("CHUNKS",)
    RETURN_NAMES = ("chunks",)
    FUNCTION = "process"
    CATEGORY = VECTORSTORE_CAT
    OUTPUT_NODE = True

    def process(self, chunk_text: str, metadata: str):
        chunks = [Chunk(text=chunk_text, metadata=metadata).json]
        return (chunks,)
