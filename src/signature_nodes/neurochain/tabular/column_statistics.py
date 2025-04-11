import pandas as pd

from ...categories import TABULAR_CAT


class ColumnStatistics:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dataframe": ("DATAFRAME", {}),
                "column": ("STRING", {"default": ""}),
                "statistic": (["min", "max", "mean", "std"], {"default": "mean"}),
            },
            "optional": {
                "use_index": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("statistic_value",)
    FUNCTION = "process"
    CATEGORY = TABULAR_CAT
    OUTPUT_NODE = True

    def process(self, dataframe: pd.DataFrame, column: str, statistic: str, use_index: bool = False):
        if use_index:
            try:
                col_index = int(column)
                series = dataframe.iloc[:, col_index]
            except ValueError:
                raise ValueError("When use_index is True, column must be a valid integer.")
        else:
            if column not in dataframe.columns:
                raise ValueError(f"Column '{column}' not found in the dataframe.")
            series = dataframe[column]

        if not pd.api.types.is_numeric_dtype(series):
            raise ValueError(f"Column '{column}' must contain numeric data.")

        if statistic == "min":
            result = series.min()
        elif statistic == "max":
            result = series.max()
        elif statistic == "mean":
            result = series.mean()
        elif statistic == "std":
            result = series.std()
        else:
            raise ValueError(f"Invalid statistic: {statistic}")

        return (float(result),)
