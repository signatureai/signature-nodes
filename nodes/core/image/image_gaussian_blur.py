import torch
from signature_core.functional.filters import gaussian_blur2d
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_CAT


class ImageGaussianBlur:
    """Applies Gaussian blur filter to an input image.

    This node performs Gaussian blur using a configurable kernel size and sigma value. Multiple passes
    can be applied for stronger blur effects. The blur is applied uniformly across all color channels.

    Args:
        image (torch.Tensor): Input image tensor in BWHC format
        radius (int): Blur kernel radius in pixels (kernel size = 2 * radius + 1)
        sigma (float): Standard deviation for Gaussian kernel, controls blur strength
        iterations (int): Number of times to apply the blur filter sequentially

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Blurred image in BWHC format with same shape as input

    Raises:
        ValueError: If image is not a torch.Tensor
        ValueError: If radius is not an integer
        ValueError: If sigma is not a float
        ValueError: If iterations is not an integer

    Notes:
        - Larger radius and sigma values produce stronger blur effects
        - Multiple iterations can create smoother results but increase processing time
        - Input image dimensions and batch size are preserved in output
        - Processing is done on GPU if input tensor is on GPU
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
                "radius": ("INT", {"default": 13}),
                "sigma": ("FLOAT", {"default": 10.5}),
                "interations": ("INT", {"default": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT

    def execute(
        self,
        image: torch.Tensor,
        radius: int = 13,
        sigma: float = 10.5,
        interations: int = 1,
    ) -> tuple[torch.Tensor]:
        tensor_image = TensorImage.from_BWHC(image)
        output = gaussian_blur2d(tensor_image, radius, sigma, interations).get_BWHC()
        return (output,)
