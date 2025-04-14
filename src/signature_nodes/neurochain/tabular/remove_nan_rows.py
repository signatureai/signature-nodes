from typing import Literal

import pandas as pd

from ...categories import TABULAR_CAT


class RemoveNaNRows:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dataframe": ("DATAFRAME", {}),
            },
            "optional": {
                "subset": ("STRING", {"default": ""}),
                "how": (["any", "all"], {"default": "any"}),
            },
        }

    RETURN_TYPES = ("DATAFRAME",)
    RETURN_NAMES = ("cleaned_dataframe",)
    FUNCTION = "process"
    CATEGORY = TABULAR_CAT
    OUTPUT_NODE = True

    def process(self, dataframe: pd.DataFrame, subset: str = "", how: Literal["any", "all"] = "any"):
        if subset:
            subset_columns = [col.strip() for col in subset.split(",")]
            if not all(col in dataframe.columns for col in subset_columns):
                raise ValueError("One or more specified columns are not in the DataFrame")
        else:
            subset_columns = None

        if subset_columns:
            cleaned_df = dataframe.dropna(subset=subset_columns, how=how)
        else:
            cleaned_df = dataframe.dropna(how=how)
        return (cleaned_df,)
