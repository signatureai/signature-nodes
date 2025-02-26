import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_CAT


class ImageSubtract:
    """Computes the absolute difference between two images.

    Performs pixel-wise subtraction between two images and takes the absolute value of the result,
    useful for comparing images or creating difference maps.

    Args:
        image_0 (torch.Tensor): First image in BWHC format
        image_1 (torch.Tensor): Second image in BWHC format to subtract from first image

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Difference image in BWHC format with same shape as inputs

    Raises:
        ValueError: If image_0 is not a torch.Tensor
        ValueError: If image_1 is not a torch.Tensor
        ValueError: If input tensors have different shapes

    Notes:
        - Both input images must have the same dimensions
        - Output values represent absolute differences between corresponding pixels
        - Useful for change detection or image comparison
        - Result is always positive due to absolute value operation
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image_0": ("IMAGE",),
                "image_1": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    DESCRIPTION = "Computes the absolute difference between two images. Performs pixel-wise subtraction and takes the absolute value of the result. Useful for comparing images, detecting changes, or creating difference maps."

    def execute(self, image_0: torch.Tensor, image_1: torch.Tensor) -> tuple[torch.Tensor]:
        image_0_tensor = TensorImage.from_BWHC(image_0)
        image_1_tensor = TensorImage.from_BWHC(image_1)
        image_tensor = torch.abs(image_0_tensor - image_1_tensor)
        output = TensorImage(image_tensor).get_BWHC()
        return (output,)
