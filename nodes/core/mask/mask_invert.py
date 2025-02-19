import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import MASK_CAT


class MaskInvert:
    """Inverts a binary mask by flipping all values.

    Creates a negative version of the input mask where white becomes black and vice versa.

    Args:
        mask (torch.Tensor): Input mask in BWHC format

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing the inverted mask

    Raises:
        ValueError: If mask is not a valid torch.Tensor

    Notes:
        - Each pixel value is subtracted from 1.0
        - Useful for creating negative space masks
        - Preserves the mask's dimensions and format
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "execute"
    CATEGORY = MASK_CAT

    def execute(self, mask: torch.Tensor) -> tuple[torch.Tensor]:
        step = TensorImage.from_BWHC(mask)
        step = 1.0 - step
        output = TensorImage(step).get_BWHC()
        return (output,)
