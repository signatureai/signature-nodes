from ...categories import MATH_CAT


class ListApplyScalarOp:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "num_list": ("LIST", {}),
                "operation": (["add", "subtract", "multiply", "divide"],),
                "scalar": ("FLOAT", {}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("num_list",)
    FUNCTION = "process"
    CATEGORY = MATH_CAT
    OUTPUT_NODE = True

    def process(self, num_list: list, operation: str, scalar: float):
        output = [None for _ in range(len(num_list))]
        for idx, value in enumerate(num_list):
            if operation == "add":
                output[idx] = value + scalar
            if operation == "subtract":
                output[idx] = value - scalar
            if operation == "multiply":
                output[idx] = value * scalar
            if operation == "divide":
                output[idx] = value / scalar
        return (output,)
