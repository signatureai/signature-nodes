import pandas as pd

from ...categories import TABULAR_CAT


class GetColumnNames:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dataframe": ("DATAFRAME", {}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("column_names",)
    FUNCTION = "process"
    CATEGORY = TABULAR_CAT
    OUTPUT_NODE = True

    def process(self, dataframe: pd.DataFrame):
        column_names = dataframe.columns.tolist()
        return (column_names,)
