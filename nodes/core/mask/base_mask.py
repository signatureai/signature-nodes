import torch
from signature_core.img.tensor_image import TensorImage

from .... import MAX_INT
from ...categories import MASK_CAT


class BaseMask:
    """Creates a basic binary mask with specified dimensions.

    A utility class that generates a simple binary mask (black or white) with user-defined dimensions.
    The mask is returned in BWHC (Batch, Width, Height, Channel) format.

    Args:
        color (str): The mask color. Options:
            - "white": Creates a mask filled with ones
            - "black": Creates a mask filled with zeros
        width (int): Width of the output mask in pixels. Default: 1024
        height (int): Height of the output mask in pixels. Default: 1024

    Returns:
        tuple[torch.Tensor]: A single-element tuple containing the binary mask tensor in BWHC format

    Raises:
        None

    Notes:
        - The output mask will have dimensions (1, 1, height, width) before BWHC conversion
        - All values in the mask are either 0 (black) or 1 (white)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "color": (["white", "black"], {"default": "white"}),
                "width": (
                    "INT",
                    {"default": 1024, "min": 1, "max": MAX_INT, "step": 1},
                ),
                "height": (
                    "INT",
                    {"default": 1024, "min": 1, "max": MAX_INT, "step": 1},
                ),
            }
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "execute"
    CATEGORY = MASK_CAT

    def execute(self, color: str = "white", width: int = 1024, height: int = 1024) -> tuple[torch.Tensor]:
        if color == "white":
            mask = torch.ones(1, 1, height, width)
        else:
            mask = torch.zeros(1, 1, height, width)
        mask = TensorImage(mask).get_BWHC()
        return (mask,)
