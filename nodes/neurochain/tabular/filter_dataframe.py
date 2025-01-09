import pandas as pd

from ...categories import TABULAR_CAT


class FilterDataFrame:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dataframe": ("DATAFRAME", {}),
                "column": ("STRING", {"default": ""}),
                "operator": (["==", "!=", ">", "<", ">=", "<=", "in", "not in"], {"default": "=="}),
                "value": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("DATAFRAME",)
    RETURN_NAMES = ("filtered_dataframe",)
    FUNCTION = "process"
    CATEGORY = TABULAR_CAT
    OUTPUT_NODE = True

    def process(self, dataframe: pd.DataFrame, column: str, operator: str, value: str):
        if operator in ["in", "not in"]:
            value = [v.strip() for v in value.split(",")]
        elif dataframe[column].dtype in ["int64", "float64"]:
            value = float(value)

        if operator == "==":
            filtered_df = dataframe[dataframe[column] == value]
        elif operator == "!=":
            filtered_df = dataframe[dataframe[column] != value]
        elif operator == ">":
            filtered_df = dataframe[dataframe[column] > value]
        elif operator == "<":
            filtered_df = dataframe[dataframe[column] < value]
        elif operator == ">=":
            filtered_df = dataframe[dataframe[column] >= value]
        elif operator == "<=":
            filtered_df = dataframe[dataframe[column] <= value]
        elif operator == "in":
            filtered_df = dataframe[dataframe[column].isin(value)]
        elif operator == "not in":
            filtered_df = dataframe[~dataframe[column].isin(value)]

        return (filtered_df,)
