import torch
from signature_core.functional.filters import unsharp_mask
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_CAT


class ImageUnsharpMask:
    """Enhances image sharpness using unsharp mask technique.

    This node applies an unsharp mask filter to enhance edge details in the image. It works by
    subtracting a blurred version of the image from the original, creating a sharpening effect.

    Args:
        image (torch.Tensor): Input image in BWHC format
        radius (int): Size of the blur kernel used in the unsharp mask
        sigma (float): Strength of the blur in the unsharp mask calculation
        iterations (int): Number of times to apply the sharpening effect

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Sharpened image in BWHC format with same shape as input

    Raises:
        ValueError: If image is not a torch.Tensor
        ValueError: If radius is not an integer
        ValueError: If sigma is not a float
        ValueError: If iterations is not an integer

    Notes:
        - Higher sigma values create stronger sharpening effects
        - Multiple iterations can create more pronounced sharpening but may introduce artifacts
        - The process preserves the original image dimensions and color range
        - Works on all color channels independently
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
                "radius": ("INT", {"default": 3}),
                "sigma": ("FLOAT", {"default": 1.5}),
                "iterations": ("INT", {"default": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    DESCRIPTION = """
    Enhances image sharpness using unsharp mask technique.
    Works by subtracting a blurred version from the original image to enhance edge details.
    Control strength with radius, sigma, and iteration count.
    """

    def execute(
        self,
        image: torch.Tensor,
        radius: int = 3,
        sigma: float = 1.5,
        iterations: int = 1,
    ) -> tuple[torch.Tensor]:
        tensor_image = TensorImage.from_BWHC(image)
        output = unsharp_mask(tensor_image, radius, sigma, iterations).get_BWHC()
        return (output,)
