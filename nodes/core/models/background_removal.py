import random

import folder_paths  # type: ignore
import torch
from signature_core.functional.transform import cutout
from signature_core.img.tensor_image import TensorImage
from signature_core.models.salient_object_detection import SalientObjectDetection

from nodes import SaveImage  # type: ignore

from ...categories import MODELS_CAT


class BackgroundRemoval(SaveImage):
    """Separates foreground subjects from image backgrounds using AI segmentation models.

    This class provides multiple AI models for background removal, offering different approaches and
    quality levels for various use cases. It can output both masked and RGBA versions of the results.

    Args:
        image (torch.Tensor): Input image tensor in BWHC (Batch, Width, Height, Channel) format.
        model_name (str): The AI model to use for segmentation. Options:
            - "inspyrenet": General-purpose segmentation
            - "rmbg14": Optimized for human subjects
            - "isnet_general": Balanced approach for various subjects
            - "fakepng": Fast but lower quality option
        preview (str): Controls preview output type. Options:
            - "mask": Shows the segmentation mask
            - "rgba": Shows the transparent background result
            - "none": No preview
        filename_prefix (str, optional): Prefix to use for saved output files. Defaults to "Signature".
        prompt (str, optional): Text prompt for metadata. Defaults to None.
        extra_pnginfo (dict, optional): Additional metadata to save with output images. Defaults to None.

    Returns:
        tuple[torch.Tensor, torch.Tensor, torch.Tensor]: A tuple containing:
            - rgba: Image with transparent background in BWHC format
            - rgb: Original image with background in BWHC format
            - mask: Binary segmentation mask in BWHC format

    Notes:
        - The model automatically handles memory cleanup after processing
        - Temporary files are saved with random suffixes to prevent naming conflicts
        - Preview images are saved at compression level 4 for balance of quality and size
        - Different models may perform better on different types of images
    """

    model_names = ["inspyrenet", "rmbg14", "isnet_general", "fakepng"]
    preview_types = ["mask", "rgba", "none"]

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + "".join(random.choice("abcdefghijklmnopqrstupvxyz") for _ in range(5))
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "model_name": (cls.model_names,),
                "preview": (cls.preview_types,),
                "image": ("IMAGE",),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    @classmethod
    def VALIDATE_INPUTS(cls, model_name: str, preview: str) -> bool:
        if not isinstance(model_name, str):
            raise ValueError("Model name must be a string")
        if not isinstance(preview, str):
            raise ValueError("Preview must be a string")
        if model_name not in cls.model_names:
            raise ValueError("Invalid model name")
        if preview not in cls.preview_types:
            raise ValueError("Invalid preview type")
        return True

    RETURN_TYPES = ("IMAGE", "IMAGE", "MASK")
    RETURN_NAMES = ("rgba", "rgb", "mask")
    FUNCTION = "execute"
    CATEGORY = MODELS_CAT
    DESCRIPTION = """
    Separates foreground subjects from image backgrounds using AI segmentation models.
    Offers multiple models with different quality levels and approaches.
    Returns the transparent background image, original image, and segmentation mask.
    """

    def execute(
        self,
        model_name: str,
        preview: str,
        image: torch.Tensor,
        prompt: str,
        extra_pnginfo: dict,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        filename_prefix = "Signature"

        model = SalientObjectDetection(model_name=model_name)
        input_image = TensorImage.from_BWHC(image)
        masks = model.forward(input_image)

        output_masks = TensorImage(masks)
        rgb, rgba = cutout(input_image, output_masks)
        rgb_output = TensorImage(rgb).get_BWHC()
        rgba_output = TensorImage(rgba).get_BWHC()
        mask_output = output_masks.get_BWHC()
        if preview == "none":
            return (
                rgba_output,
                rgb_output,
                mask_output,
            )
        preview_images = output_masks.get_rgb_or_rgba().get_BWHC() if preview == "mask" else rgba_output
        result = self.save_images(preview_images, filename_prefix, prompt, extra_pnginfo)
        result.update(
            {
                "result": (
                    rgba_output,
                    rgb_output,
                    mask_output,
                )
            }
        )
        model = None
        del model
        return result
