import torch
from signature_core.functional.filters import gaussian_blur2d
from signature_core.img.tensor_image import TensorImage

from ...categories import MASK_CAT


class MaskGaussianBlur:
    """Applies Gaussian blur to soften mask edges and create smooth transitions.

    Implements a configurable Gaussian blur with control over blur radius, strength, and iterations.

    Args:
        image (torch.Tensor): Input mask in BWHC format
        radius (int): Blur kernel radius. Default: 13
        sigma (float): Blur strength/standard deviation. Default: 10.5
        iterations (int): Number of blur passes to apply. Default: 1
        only_outline (bool): Whether to blur only the mask edges. Default: False

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing the blurred mask

    Raises:
        ValueError: If image is not a valid torch.Tensor

    Notes:
        - Larger radius values create wider blur effects
        - Multiple iterations can create stronger blur effects
        - Sigma controls the falloff of the blur effect
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "radius": ("INT", {"default": 13}),
                "sigma": ("FLOAT", {"default": 10.5}),
                "iterations": ("INT", {"default": 1}),
            }
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "execute"
    CATEGORY = MASK_CAT
    DESCRIPTION = """
    Applies Gaussian blur to soften mask edges and create smooth transitions.
    Configurable blur with control over radius, strength, and number of iterations.
    Useful for creating gradual falloff at mask boundaries.
    """

    def execute(
        self,
        mask: torch.Tensor,
        radius: int = 13,
        sigma: float = 10.5,
        iterations: int = 1,
    ) -> tuple[torch.Tensor]:
        tensor_image = TensorImage.from_BWHC(mask)
        output = gaussian_blur2d(tensor_image, radius, sigma, iterations).get_BWHC()
        return (output,)
