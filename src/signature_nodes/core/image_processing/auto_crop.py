import torch
from signature_core.functional.color import rgba_to_rgb
from signature_core.functional.transform import auto_crop
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_PROCESSING_CAT


class AutoCrop:
    """Automatically crops an image based on a mask content.

    This node detects non-zero regions in a mask and crops both the image and mask
    to those regions, with optional padding. Useful for removing empty space around
    subjects or focusing on specific masked areas.

    Args:
        image (torch.Tensor): Input image tensor in BWHC format with values in range [0, 1]
        mask (torch.Tensor): Input mask tensor in BWHC format with values in range [0, 1]
        mask_threshold (float): Minimum mask value to consider as content (0.0-1.0)
        left_padding (int): Additional pixels to include on the left side
        right_padding (int): Additional pixels to include on the right side
        top_padding (int): Additional pixels to include on the top
        bottom_padding (int): Additional pixels to include on the bottom

    Returns:
        tuple:
            - cropped_image (torch.Tensor): Cropped image in BWHC format
            - cropped_mask (torch.Tensor): Cropped mask in BWHC format
            - x (int): X-coordinate of crop start in original image
            - y (int): Y-coordinate of crop start in original image
            - width (int): Width of cropped region
            - height (int): Height of cropped region

    Raises:
        ValueError: If mask and image dimensions don't match
        RuntimeError: If no content is found in mask above threshold

    Notes:
        - Input tensors should be in BWHC format (Batch, Width, Height, Channels)
        - Mask should be single-channel
        - All padding values must be non-negative
        - If mask is empty above threshold, may return minimal crop
        - Coordinates are returned relative to original image
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "mask_threshold": (
                    "FLOAT",
                    {"default": 0.1, "min": 0.00, "max": 1.00, "step": 0.01},
                ),
                "left_padding": ("INT", {"default": 0}),
                "right_padding": ("INT", {"default": 0}),
                "top_padding": ("INT", {"default": 0}),
                "bottom_padding": ("INT", {"default": 0}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("cropped_image", "cropped_mask", "x", "y", "width", "height")

    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT
    DESCRIPTION = """
    Automatically crops images based on mask content.
    Detects non-zero regions in a mask and crops both image and mask to those regions with optional padding.
    Returns crop coordinates for further processing.
    """

    def execute(
        self,
        image: torch.Tensor,
        mask: torch.Tensor,
        mask_threshold: float = 0.1,
        left_padding: int = 0,
        right_padding: int = 0,
        top_padding: int = 0,
        bottom_padding: int = 0,
    ) -> tuple[torch.Tensor, torch.Tensor, int, int, int, int]:
        img_tensor = TensorImage.from_BWHC(image)
        mask_tensor = TensorImage.from_BWHC(mask)
        if img_tensor.shape[1] != 3:
            img_tensor = rgba_to_rgb(img_tensor)

        padding = (
            left_padding,
            right_padding,
            top_padding,
            bottom_padding,
        )
        img_result, mask_result, min_x, min_y, width, height = auto_crop(
            img_tensor, mask_tensor, mask_threshold=mask_threshold, padding=padding
        )
        output_img = TensorImage(img_result).get_BWHC()
        output_mask = TensorImage(mask_result).get_BWHC()

        return (output_img, output_mask, min_x, min_y, width, height)
