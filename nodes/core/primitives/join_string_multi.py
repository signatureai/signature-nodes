from ...categories import PRIMITIVES_CAT


class JoinStringMulti:
    """
    Creates single string, or a list of strings, from
    multiple input strings.
    You can set how many inputs the node has,
    with the **inputcount** and clicking update.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "inputcount": ("INT", {"default": 2, "min": 2, "max": 1000, "step": 1}),
                "delimiter": ("STRING", {"default": " ", "multiline": False}),
                "return_list": ("BOOLEAN", {"default": False}),
                "string_1": ("STRING", {"default": "", "forceInput": True}),
                "string_2": ("STRING", {"default": "", "forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "combine"
    CATEGORY = PRIMITIVES_CAT
    DESCRIPTION = "Creates single string, or a list of strings, from multiple input strings. You can set how many inputs the node has, with the **inputcount** and clicking update."

    def combine(
        self,
        inputcount: int = 2,
        delimiter: str = " ",
        return_list: bool = False,
        **kwargs,
    ) -> tuple[str] | tuple[list[str]]:
        string = kwargs["string_1"]
        strings = [string]  # Initialize a list with the first string
        for c in range(1, inputcount):
            new_string = kwargs[f"string_{c + 1}"]
            if return_list:
                strings.append(new_string)  # Add new string to the list
            else:
                string = string + delimiter + new_string
        if return_list:
            return (strings,)  # Return the list of strings
        else:
            return (string,)  # Return the combined string
