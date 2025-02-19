from typing import Optional

import torch
from signature_core.functional.transform import rotate
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_PROCESSING_CAT


class Rotate:
    """Rotates images and masks by a specified angle with optional zoom adjustment.

    Performs rotation of images and masks with control over whether to zoom to fit
    the entire rotated content. Useful for reorienting content while managing the
    trade-off between content preservation and output size.

    Args:
        image (torch.Tensor, optional): Input image in BWHC format with values in range [0, 1]
        mask (torch.Tensor, optional): Input mask in BWHC format with values in range [0, 1]
        angle (float): Rotation angle in degrees (0-360)
        zoom_to_fit (bool): Whether to zoom out to show all rotated content

    Returns:
        tuple:
            - image (torch.Tensor): Rotated image in BWHC format
            - mask (torch.Tensor): Rotated mask in BWHC format

    Raises:
        ValueError: If neither image nor mask is provided
        ValueError: If angle is outside valid range
        RuntimeError: If input tensors have invalid dimensions

    Notes:
        - At least one of image or mask must be provided
        - Rotation is performed counterclockwise
        - When zoom_to_fit is False, corners may be clipped
        - When zoom_to_fit is True, output may be larger
        - Interpolation is bilinear for smooth results
        - Empty areas after rotation are filled with black
        - Maintains aspect ratio of input
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "image": ("IMAGE", {"default": None}),
                "mask": ("MASK", {"default": None}),
                "angle": (
                    "FLOAT",
                    {"default": 0.0, "min": 0, "max": 360.0, "step": 1.0},
                ),
                "zoom_to_fit": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT

    def execute(
        self,
        image: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        angle: float = 0.0,
        zoom_to_fit: bool = False,
    ):
        input_image = (
            TensorImage.from_BWHC(image) if isinstance(image, torch.Tensor) else TensorImage(torch.zeros((1, 3, 1, 1)))
        )
        input_mask = (
            TensorImage.from_BWHC(mask) if isinstance(mask, torch.Tensor) else TensorImage(torch.zeros((1, 1, 1, 1)))
        )
        output_image = rotate(input_image, angle, zoom_to_fit).get_BWHC()
        output_mask = rotate(input_mask, angle, zoom_to_fit).get_BWHC()

        return (
            output_image,
            output_mask,
        )
