from ...categories import PRIMITIVES_CAT


class Int:
    """A node that handles integer number inputs with configurable parameters.

    This node provides functionality for processing integer numbers within a specified range
    and step size. It can be used as a basic input node in computational graphs where whole
    number values are required.

    Args:
        value (int): The input integer number to process.
                    Default: 0
                    Min: -18446744073709551615
                    Max: 18446744073709551615
                    Step: 1

    Returns:
        tuple[int]: A single-element tuple containing the processed integer value.

    Notes:
        - The node maintains the exact input value without any transformation
        - The step value of 1 ensures whole number increments
        - The min/max values correspond to the 64-bit integer limits
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": (
                    "INT",
                    {
                        "default": 0,
                        "min": -18446744073709551615,
                        "max": 18446744073709551615,
                        "step": 1,
                    },
                ),
            },
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = PRIMITIVES_CAT

    def execute(self, value: int = 0) -> tuple[int]:
        return (value,)
