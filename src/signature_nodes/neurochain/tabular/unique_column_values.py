import pandas as pd

from ...categories import TABULAR_CAT


class UniqueColumnValues:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dataframe": ("DATAFRAME", {}),
                "column": ("STRING", {"default": ""}),
            },
            "optional": {
                "use_index": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("unique_values",)
    FUNCTION = "process"
    CATEGORY = TABULAR_CAT
    OUTPUT_NODE = True

    def process(self, dataframe: pd.DataFrame, column: str, use_index: bool = False):
        if use_index:
            try:
                col_index = int(column)
                unique_values = dataframe.iloc[:, col_index].unique().tolist()
            except ValueError:
                raise ValueError("When use_index is True, column must be a valid integer.")
        else:
            if column not in dataframe.columns:
                raise ValueError(f"Column '{column}' not found in the dataframe.")
            unique_values = dataframe[column].unique().tolist()

        return (unique_values,)
