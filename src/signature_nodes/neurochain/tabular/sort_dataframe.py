import pandas as pd

from ...categories import TABULAR_CAT


class SortDataFrame:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dataframe": ("DATAFRAME", {}),
                "column": ("STRING", {"default": ""}),
                "ascending": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("DATAFRAME",)
    RETURN_NAMES = ("sorted_dataframe",)
    FUNCTION = "process"
    CATEGORY = TABULAR_CAT
    OUTPUT_NODE = True

    def process(self, dataframe: pd.DataFrame, column: str, ascending: bool):
        sorted_df = dataframe.sort_values(by=column, ascending=ascending)
        return (sorted_df,)
