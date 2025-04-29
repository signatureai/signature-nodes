import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import FILE_CAT
from .shared import image_array_to_tensor


class ImageFromWeb:
    """Fetches and converts web images to ComfyUI-compatible tensors.

    Downloads an image from a URL and processes it into ComfyUI's expected tensor format. Handles both RGB
    and RGBA images with automatic mask generation for transparency.

    Args:
        url (str): Direct URL to the image file (PNG, JPG, JPEG, WebP).

    Returns:
        tuple[torch.Tensor, torch.Tensor]:
            - image: BWHC format tensor, normalized to [0,1] range
            - mask: BWHC format tensor for transparency/alpha channel

    Raises:
        ValueError: If URL is invalid, inaccessible, or not a string
        HTTPError: If image download fails
        IOError: If image format is unsupported

    Notes:
        - Automatically converts images to float32 format
        - RGB images get a mask of ones
        - RGBA images use alpha channel as mask
        - Supports standard web image formats
        - Image dimensions are preserved
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {"required": {"url": ("STRING", {"default": "URL HERE"})}}

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "execute"
    CATEGORY = FILE_CAT
    DESCRIPTION = """
    Downloads and converts web images to ComfyUI-compatible tensors.
    Fetches images from URLs and processes them with automatic mask generation for transparency.
    Supports common web image formats.
    """

    def execute(self, url: str = "URL HERE") -> tuple[torch.Tensor, torch.Tensor]:
        img_arr = TensorImage.from_web(url)
        return image_array_to_tensor(img_arr)
