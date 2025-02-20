import random
from typing import Optional

import folder_paths  # type: ignore
import torch
from signature_core.img.tensor_image import TensorImage

from nodes import SaveImage  # type: ignore

from ...categories import MASK_CAT


class MaskPreview(SaveImage):
    """Generates and saves a visual preview of a mask as an image file.

    Converts mask data to a viewable image format and saves it with optional metadata.

    Args:
        mask (torch.Tensor): Input mask in BWHC format
        filename_prefix (str): Prefix for the output filename. Default: "Signature"
        prompt (Optional[str]): Optional prompt text to include in metadata
        extra_pnginfo (Optional[dict]): Additional PNG metadata to include

    Returns:
        tuple[str, str]: Tuple containing paths to the saved preview images

    Raises:
        ValueError: If mask is not a valid torch.Tensor
        IOError: If unable to save the preview image

    Notes:
        - Saves to temporary directory with random suffix
        - Converts mask to RGB/RGBA format for viewing
        - Includes compression level 4 for storage efficiency
    """

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + "".join(random.choice("abcdefghijklmnopqrstupvxyz") for _ in range(5))
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    FUNCTION = "execute"
    CATEGORY = MASK_CAT

    def execute(
        self,
        mask: torch.Tensor,
        prompt: Optional[str] = None,
        extra_pnginfo: Optional[dict] = None,
    ) -> dict[str, dict[str, list]]:
        preview = TensorImage.from_BWHC(mask).get_rgb_or_rgba().get_BWHC()
        return self.save_images(preview, "Signature", prompt, extra_pnginfo)
