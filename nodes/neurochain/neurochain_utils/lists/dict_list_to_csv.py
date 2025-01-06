import csv
from io import StringIO

from ....categories import LISTS_CAT


class DictListToCsv:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dict_list": ("LIST",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("csv_string",)
    FUNCTION = "process"
    CATEGORY = LISTS_CAT
    OUTPUT_NODE = True

    def process(self, dict_list: list):
        fields = dict_list[0].keys()
        stringBuilder = StringIO()
        csvwriter = csv.DictWriter(stringBuilder, fieldnames=fields)

        csvwriter.writeheader()
        csvwriter.writerows(dict_list)

        csv_string = stringBuilder.getvalue()

        return (csv_string,)
