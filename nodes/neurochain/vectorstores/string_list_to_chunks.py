from neurochain.utils.utils import Chunk

from ...categories import UTILS_CAT


class StringListToChunks:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"string_list": ("LIST", {}), "metadata_list": ("LIST", {})}}

    RETURN_TYPES = ("CHUNKS",)
    RETURN_NAMES = ("chunks",)
    FUNCTION = "process"
    CATEGORY = UTILS_CAT
    OUTPUT_NODE = True

    def process(self, string_list: list, metadata_list: list):
        chunks: list[str | None] = [None for _ in range(len(string_list))]
        for idx, string in enumerate(string_list):
            chunks[idx] = Chunk(text=string, metadata=metadata_list[idx]).json
        return (chunks,)
