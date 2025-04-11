import torch

from ...categories import IMAGE_CAT


class GetImageShape:
    """Analyzes and returns the dimensions of an input image.

    Extracts and returns detailed shape information from an input image tensor, providing both
    individual dimensions and a formatted string representation.

    Args:
        image (torch.Tensor): Input image in BWHC format to analyze

    Returns:
        tuple[int, int, int, int, str]: Five-element tuple containing:
            - int: Batch size (B dimension)
            - int: Width in pixels
            - int: Height in pixels
            - int: Number of channels (typically 3 for RGB, 4 for RGBA)
            - str: Formatted string showing complete shape (B,W,H,C)

    Raises:
        ValueError: If image is not a torch.Tensor
        ValueError: If image does not have exactly 4 dimensions

    Notes:
        - Useful for debugging and dynamic processing
        - Shape string provides human-readable format
        - Can handle both RGB and RGBA images
        - Validates correct tensor format
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("batch", "width", "height", "channels", "debug")
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    CLASS_ID = "get_image_size"
    DESCRIPTION = """
    Analyzes and returns the dimensions of an input image.
    Extracts batch size, width, height, channels, and a formatted shape string.
    Useful for debugging and dynamic image processing workflows.
    """

    def execute(self, image: torch.Tensor) -> tuple[int, int, int, int, str]:
        return (
            image.shape[0],
            image.shape[2],
            image.shape[1],
            image.shape[3],
            str(image.shape),
        )
