import pandas as pd

from ...categories import TABULAR_CAT


class GetDataFrameColumn:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dataframe": ("DATAFRAME", {}),
                "column_identifier": ("STRING", {"default": ""}),
            },
            "optional": {
                "use_index": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("LIST", "STRING")
    RETURN_NAMES = ("column_data", "column_name")
    FUNCTION = "process"
    CATEGORY = TABULAR_CAT
    OUTPUT_NODE = True

    def process(self, dataframe: pd.DataFrame, column_identifier: str, use_index: bool = False):
        if use_index:
            try:
                index = int(column_identifier)
                column_data = dataframe.iloc[:, index].tolist()
                column_name = dataframe.columns[index]
            except ValueError:
                raise ValueError("When use_index is True, column_identifier must be a valid integer.")
            except IndexError:
                raise IndexError(
                    f"Column index {index} is out of bounds for dataframe with {len(dataframe.columns)} columns."
                )
        else:
            if column_identifier not in dataframe.columns:
                raise ValueError(f"Column '{column_identifier}' not found in the dataframe.")
            column_data = dataframe[column_identifier].tolist()
            column_name = column_identifier

        return (column_data, column_name)
