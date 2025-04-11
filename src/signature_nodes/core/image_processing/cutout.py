from typing import Optional

import torch
from signature_core.functional.transform import cutout
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_PROCESSING_CAT


class Cutout:
    """Creates masked cutouts from images with both RGB and RGBA outputs.

    Extracts portions of an image based on a mask, providing both RGB and RGBA
    versions of the result. Useful for isolating subjects or creating transparent
    cutouts for compositing.

    Args:
        image (torch.Tensor): Input image in BWHC format with values in range [0, 1]
        mask (torch.Tensor): Binary or continuous mask in BWHC format with values in range [0, 1]

    Returns:
        tuple:
            - rgb (torch.Tensor): Masked image in RGB format (BWHC)
            - rgba (torch.Tensor): Masked image in RGBA format (BWHC)

    Raises:
        ValueError: If either image or mask is not provided
        ValueError: If input tensors have mismatched dimensions
        RuntimeError: If input tensors have invalid dimensions

    Notes:
        - Mask values determine transparency in RGBA output
        - RGB output has masked areas filled with black
        - RGBA output preserves partial mask values as alpha
        - Input image must be 3 channels (RGB)
        - Input mask must be 1 channel
        - Output maintains original image resolution
        - All non-zero mask values are considered for cutout
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
            },
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("rgb", "rgba")
    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT
    DESCRIPTION = """
    Creates masked cutouts from images with both RGB and RGBA outputs.
    Extracts portions of an image based on a mask,
    useful for isolating subjects or creating transparent cutouts for compositing.
    """

    def execute(
        self,
        image: Optional[torch.Tensor],
        mask: Optional[torch.Tensor],
    ):
        if not isinstance(image, torch.Tensor) or not isinstance(mask, torch.Tensor):
            raise ValueError("Either image or mask must be provided")

        tensor_image = TensorImage.from_BWHC(image)
        tensor_mask = TensorImage.from_BWHC(mask, image.device)

        image_rgb, image_rgba = cutout(tensor_image, tensor_mask)

        out_image_rgb = TensorImage(image_rgb).get_BWHC()
        out_image_rgba = TensorImage(image_rgba).get_BWHC()

        return (
            out_image_rgb,
            out_image_rgba,
        )
