import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import FILE_CAT
from .shared import image_array_to_tensor


class ImageFromBase64:
    """Converts base64 image strings to ComfyUI-compatible tensors.

    Processes base64-encoded image data into tensor format suitable for ComfyUI operations. Handles
    both RGB and RGBA images with proper mask generation.

    Args:
        base64 (str): Raw base64-encoded image string without data URL prefix.

    Returns:
        tuple[torch.Tensor, torch.Tensor]:
            - image: BWHC format tensor, normalized to [0,1] range
            - mask: BWHC format tensor for transparency/alpha channel

    Raises:
        ValueError: If base64 string is invalid or not a string
        IOError: If decoded image format is unsupported
        binascii.Error: If base64 decoding fails

    Notes:
        - Converts decoded images to float32 format
        - RGB images get a mask of ones
        - RGBA images use alpha channel as mask
        - Supports common image formats (PNG, JPG, JPEG)
        - Original image dimensions are preserved
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {"required": {"base64": ("STRING", {"default": "BASE64 HERE", "multiline": True})}}

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "execute"
    CATEGORY = FILE_CAT
    DEPRECATED = True

    def execute(self, base64: str = "BASE64 HERE") -> tuple[torch.Tensor, torch.Tensor]:
        img_arr = TensorImage.from_base64(base64)
        return image_array_to_tensor(img_arr)
