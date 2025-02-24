import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import MASK_CAT


class MaskDistance:
    """Calculates the Euclidean distance between two binary masks.

    Computes the average pixel-wise Euclidean distance between two masks, useful for comparing
    mask similarity or differences.

    Args:
        mask_0 (torch.Tensor): First input mask in BWHC format
        mask_1 (torch.Tensor): Second input mask in BWHC format

    Returns:
        tuple[float]: A single-element tuple containing the computed distance value

    Raises:
        ValueError: If either mask_0 or mask_1 is not a valid torch.Tensor

    Notes:
        - Distance is calculated as the root mean square difference between mask pixels
        - Output is normalized and returned as a single float value
        - Smaller values indicate more similar masks
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"mask_0": ("MASK",), "mask_1": ("MASK",)}}

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = MASK_CAT

    def execute(self, mask_0: torch.Tensor, mask_1: torch.Tensor) -> tuple[torch.Tensor]:
        tensor1 = TensorImage.from_BWHC(mask_0)
        tensor2 = TensorImage.from_BWHC(mask_1)

        try:
            dist = torch.Tensor((tensor1 - tensor2).pow(2).sum(3).sqrt().mean())
        except RuntimeError:
            raise ValueError("Invalid mask dimensions")
        return (dist,)
