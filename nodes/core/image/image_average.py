from typing import Optional

import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_CAT


class ImageAverage:
    """Calculates the average color of an input image.

    Computes the mean color values across all pixels in the image, resulting in a uniform color
    image representing the average color of the input.

    Args:
        image (torch.Tensor): Input image in BWHC format to calculate average from
        focus_mask (torch.Tensor, optional): Mask to focus calculation on specific areas

    Returns:
        tuple[torch.Tensor, str]: Two-element tuple containing:
            - tensor: Uniform color image in BWHC format with same shape as input
            - str: Hexadecimal color code of the average color

    Raises:
        ValueError: If image is not a torch.Tensor

    Notes:
        - Output maintains the same dimensions as input but with uniform color
        - Calculation is performed per color channel
        - Useful for color analysis or creating color-matched solid backgrounds
        - Preserves the original batch size
        - When focus_mask is provided, only calculates average from masked areas
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "focus_mask": ("MASK",),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("color", "hex_color")
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    DESCRIPTION = """
    Calculates the average color of an input image, creating a uniform color image.
    Optionally uses a mask to focus on specific areas. Returns both the color image
    and hexadecimal color code.
    """

    def execute(self, image: torch.Tensor, focus_mask: Optional[torch.Tensor] = None) -> tuple[torch.Tensor, str]:
        step = TensorImage.from_BWHC(image)
        if focus_mask is not None:
            mask = TensorImage.from_BWHC(focus_mask)
            masked_image = step * mask
            step = masked_image.sum(dim=[2, 3], keepdim=True) / (mask.sum(dim=[2, 3], keepdim=True) + 1e-8)
        else:
            step = step.mean(dim=[2, 3], keepdim=True)
        step = step.expand(-1, -1, image.shape[1], image.shape[2])
        output = TensorImage(step).get_BWHC()

        avg_color = step[0, :, 0, 0] * 255
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(avg_color[0].item()), int(avg_color[1].item()), int(avg_color[2].item())
        )

        return (output, hex_color)
