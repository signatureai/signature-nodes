import pandas as pd

from ...categories import TABULAR_CAT


class SaveCSV:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dataframe": ("DATAFRAME", {}),
                "file_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "encoding": ("STRING", {"default": "utf-8"}),
                "separator": ("STRING", {"default": ","}),
                "index": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_path",)
    FUNCTION = "process"
    CATEGORY = TABULAR_CAT
    OUTPUT_NODE = True

    def process(
        self,
        dataframe: pd.DataFrame,
        file_path: str,
        encoding: str = "utf-8",
        separator: str = ",",
        index: bool = False,
    ):
        dataframe.to_csv(file_path, encoding=encoding, sep=separator, index=index)
        return (file_path,)
