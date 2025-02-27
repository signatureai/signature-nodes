import random
from typing import Optional

import folder_paths  # type: ignore
import torch
from signature_core.img.tensor_image import TensorImage
from signature_core.models.seemore import SeeMore

from nodes import SaveImage  # type: ignore

from ...categories import MODELS_CAT


class Unblur(SaveImage):
    """Enhances image clarity by reducing blur using the SeeMore model.

    This class implements image deblurring functionality using the SeeMore neural network model.
    It's effective for correcting motion blur, out-of-focus areas, and general image softness.

    Args:
        image (torch.Tensor): Input image tensor in BWHC (Batch, Width, Height, Channel) format.
        preview (str): Controls preview image generation. Options:
            - "on": Saves preview images
            - "off": No preview images
        filename_prefix (str, optional): Prefix to use for saved output files. Defaults to "Signature".
        prompt (str, optional): Text prompt for metadata. Defaults to None.
        extra_pnginfo (dict, optional): Additional metadata to save with output images. Defaults to None.

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing the unblurred image in BWHC format.

    Notes:
        - The model automatically handles memory cleanup after processing
        - Temporary files are saved with random suffixes to prevent naming conflicts
        - Preview images are saved at compression level 4 for balance of quality and size
    """

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + "".join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
                "preview": (["on", "off"],),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = MODELS_CAT
    DEPRECATED = True
    DESCRIPTION = "Enhances image clarity by reducing blur using the SeeMore neural network model. Effective for correcting motion blur, out-of-focus areas, and general image softness. Provides optional preview generation."

    def execute(
        self,
        image: torch.Tensor,
        preview: str = "on",
        prompt: Optional[str] = None,
        extra_pnginfo: Optional[dict] = None,
    ):
        if preview not in ["on", "off"]:
            raise ValueError("Preview must be either 'on' or 'off'")

        filename_prefix = "Signature"

        model = SeeMore()
        input_image = TensorImage.from_BWHC(image)
        output_image = model.forward(input_image)
        output_images = TensorImage(output_image).get_BWHC()

        if preview == "off":
            return (output_images,)
        result = self.save_images(output_images, filename_prefix, prompt, extra_pnginfo)
        result.update({"result": (output_images,)})
        model = None
        del model
        return result
