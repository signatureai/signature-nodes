from ...categories import PRIMITIVES_CAT


class Float:
    """A node that handles floating-point number inputs with configurable parameters.

    This node provides functionality for processing floating-point numbers within a specified range
    and step size. It can be used as a basic input node in computational graphs where decimal
    number precision is required.

    Args:
        value (float): The input floating-point number to process.
                      Default: 0
                      Min: -18446744073709551615
                      Max: 18446744073709551615
                      Step: 0.01

    Returns:
        tuple[float]: A single-element tuple containing the processed float value.

    Notes:
        - The node maintains the exact input value without any transformation
        - The step value of 0.01 provides two decimal places of precision by default
        - The min/max values correspond to the 64-bit integer limits
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -18446744073709551615,
                        "max": 18446744073709551615,
                        "step": 0.01,
                    },
                ),
            },
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = PRIMITIVES_CAT

    def execute(self, value: float = 0) -> tuple[float]:
        return (value,)
