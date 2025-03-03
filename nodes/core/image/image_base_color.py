import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_CAT


class ImageBaseColor:
    """Creates a solid color image with specified dimensions.

    This node generates a uniform color image using a hex color code. The output is a tensor in BWHC
    format (Batch, Width, Height, Channels) with the specified dimensions.

    Args:
        hex_color (str): Hex color code in format "#RRGGBB" (e.g., "#FFFFFF" for white)
        width (int): Width of the output image in pixels
        height (int): Height of the output image in pixels

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Image in BWHC format with shape (1, height, width, 3)

    Raises:
        ValueError: If width or height are not integers
        ValueError: If hex_color is not a string
        ValueError: If hex_color is not in valid "#RRGGBB" format

    Notes:
        - The output tensor values are normalized to range [0, 1]
        - Alpha channel is not supported
        - The batch dimension is always 1
        - RGB values are extracted from hex color and converted to float32
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "hex_color": ("STRING", {"default": "#FFFFFF"}),
                "width": ("INT", {"default": 1024}),
                "height": ("INT", {"default": 1024}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    CLASS_ID = "image_base_color"
    DESCRIPTION = "Creates a solid color image with specified dimensions. Generates a uniform color image using a hex color code (#RRGGBB format). Useful for backgrounds, color testing, or as base layers for compositing."

    def execute(self, hex_color: str = "#FFFFFF", width: int = 1024, height: int = 1024) -> tuple[torch.Tensor]:
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        # Create a tensor with the specified color
        color_tensor = torch.tensor([r, g, b], dtype=torch.float32) / 255.0

        # Reshape to (3, 1, 1) and expand to (3, H, W)
        color_tensor = color_tensor.view(3, 1, 1).expand(3, height, width)

        # Repeat for the batch size
        batch_tensor = color_tensor.unsqueeze(0).expand(1, -1, -1, -1)

        output = TensorImage(batch_tensor).get_BWHC()
        return (output,)
