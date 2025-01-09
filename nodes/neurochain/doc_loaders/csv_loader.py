from neurochain.document_loaders.csv_loader import CsvLoader as CsvLoaderCore

from ...categories import LOADERS_CAT


class CsvLoader:
    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "path": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("CHUNKS",)
    RETURN_NAMES = ("chunks",)
    FUNCTION = "process"
    CATEGORY = LOADERS_CAT
    OUTPUT_NODE = True

    def process(self, path: str):
        chunks = CsvLoaderCore.build_chunks(path, chunk_ignore_cols=["country name"])
        return (chunks,)
