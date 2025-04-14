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
        value_transformed: str | list[str] | float = value
        if operator in ["in", "not in"]:
            value_transformed = [v.strip() for v in value.split(",")]
        elif dataframe[column].dtype in ["int64", "float64"]:
            value_transformed = float(value)

        if operator == "==":
            filtered_df = dataframe[dataframe[column] == value_transformed]
        elif operator == "!=":
            filtered_df = dataframe[dataframe[column] != value_transformed]
        elif operator == ">":
            filtered_df = dataframe[dataframe[column] > value_transformed]
        elif operator == "<":
            filtered_df = dataframe[dataframe[column] < value_transformed]
        elif operator == ">=":
            filtered_df = dataframe[dataframe[column] >= value_transformed]
        elif operator == "<=":
            filtered_df = dataframe[dataframe[column] <= value_transformed]
        elif operator == "in" and isinstance(value_transformed, list):
            filtered_df = dataframe[dataframe[column].isin(value_transformed)]
        elif operator == "not in" and isinstance(value_transformed, list):
            filtered_df = dataframe[~dataframe[column].isin(value_transformed)]

        return (filtered_df,)
