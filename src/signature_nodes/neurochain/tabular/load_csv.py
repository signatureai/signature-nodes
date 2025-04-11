import pandas as pd

from ...categories import TABULAR_CAT


class LoadCSV:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "encoding": ("STRING", {"default": "utf-8"}),
                "separator": ("STRING", {"default": ","}),
            },
        }

    RETURN_TYPES = ("DATAFRAME",)
    RETURN_NAMES = ("dataframe",)
    FUNCTION = "process"
    CATEGORY = TABULAR_CAT
    OUTPUT_NODE = True

    def process(self, file_path: str, encoding: str = "utf-8", separator: str = ","):
        df = pd.read_csv(file_path, encoding=encoding, sep=separator)
        return (df,)
