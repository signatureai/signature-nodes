import re

from ....categories import LISTS_CAT


class BulkFormat:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dict_list": ("LIST", {}),
                "template": ("STRING", {"multiline": True, "default": "Use [keyword] to fill template"}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("string_list",)
    FUNCTION = "process"
    CATEGORY = LISTS_CAT
    OUTPUT_NODE = True

    def process(self, dict_list: list, template: str):
        def exp_recursive(dct, t_str):
            for k, val in dct.items():
                match val:
                    case str():
                        pattern = re.compile(r"\[{}\]".format(k))
                        t_str = pattern.sub(val, t_str)
                    case dict():
                        dic_attern = re.compile(r"\[{}\[([^\[\]]+)\]\]".format(k))
                        kk = dic_attern.findall(t_str)
                        for match in kk:
                            if match in val:
                                di = val[match]
                                full_placeholder = f"[{k}[{match}]]"
                                if isinstance(di, dict):
                                    t_str = exp_recursive(di, t_str)
                                else:
                                    t_str = t_str.replace(full_placeholder, di)
            return t_str

        results = [None for _ in range(len(dict_list))]

        # pattern = r'\[(.*?)\]'  # Regular expression pattern to find substrings inside []
        # required_keys = re.findall(pattern, template)
        # print(required_keys)

        for idx, dict_obj in enumerate(dict_list):
            print(dict_obj)
            print(template)
            result = template

            # for key in required_keys:
            #     result = result.replace(f'[{key}]', dict_obj[key])

            result = exp_recursive(dict_obj, template)

            results[idx] = result
            print(result)
        return (results,)
