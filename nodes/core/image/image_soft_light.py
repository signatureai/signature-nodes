import torch
from signature_core.functional.filters import image_soft_light
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_CAT


class ImageSoftLight:
    """Applies soft light blend mode between two images.

    Implements the soft light blending mode similar to photo editing software. The effect creates a
    subtle, soft lighting effect based on the interaction between the top and bottom layers.

    Args:
        top (torch.Tensor): Top layer image in BWHC format, acts as the blend layer
        bottom (torch.Tensor): Bottom layer image in BWHC format, acts as the base layer

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Blended image in BWHC format with same shape as inputs

    Raises:
        ValueError: If top is not a torch.Tensor
        ValueError: If bottom is not a torch.Tensor
        ValueError: If input tensors have different shapes

    Notes:
        - Both input images must have the same dimensions
        - The blend preserves the original image dimensions and color range
        - The effect is similar to soft light blend mode in photo editing software
        - Processing is done on GPU if input tensors are on GPU
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "top": ("IMAGE",),
                "bottom": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    DESCRIPTION = "Applies soft light blend mode between two images. Creates subtle lighting effects based on the interaction between top and bottom layers. Similar to soft light blending in photo editing software."

    def execute(self, top: torch.Tensor, bottom: torch.Tensor) -> tuple[torch.Tensor]:
        top_tensor = TensorImage.from_BWHC(top)
        bottom_tensor = TensorImage.from_BWHC(bottom)
        output = image_soft_light(top_tensor, bottom_tensor).get_BWHC()

        return (output,)
