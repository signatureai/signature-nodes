import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import MASK_CAT


class MaskBinaryFilter:
    """Applies binary thresholding to convert a grayscale mask into a binary mask.

    Converts all values above threshold to 1 and below threshold to 0, creating a strict
    binary mask.

    Args:
        mask (torch.Tensor): Input mask in BWHC format
        threshold (float): Threshold value for binary conversion. Default: 0.01

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing the binary mask

    Raises:
        ValueError: If mask is not a valid torch.Tensor

    Notes:
        - Values > threshold become 1.0
        - Values ≤ threshold become 0.0
        - Useful for cleaning up masks with intermediate values
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "threshold": (
                    "FLOAT",
                    {"default": 0.01, "min": 0.00, "max": 1.00, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "execute"
    CATEGORY = MASK_CAT

    def execute(self, mask: torch.Tensor, threshold: float = 0.01) -> tuple[torch.Tensor]:
        step = TensorImage.from_BWHC(mask)
        step[step > threshold] = 1.0
        step[step <= threshold] = 0.0
        output = TensorImage(step).get_BWHC()
        return (output,)
