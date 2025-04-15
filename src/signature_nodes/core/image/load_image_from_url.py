from typing import Any, Optional

import torch
from signature_core.functional.color import rgb_to_grayscale
from signature_core.functional.transform import cutout
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_CAT
from ...shared import any_type


class LoadImageFromURL:
    """Loads and processes images from URLs for ComfyUI workflows.

    This node fetches images from web URLs and prepares them for use in ComfyUI.
    Supports single or multiple images, handling of transparency, and conversion
    to masks when needed.

    Args:
        subtype (str): "image" for regular images or "mask" for grayscale masks.
        include_alpha (bool): Whether to preserve the alpha/transparency channel.
        multiple (bool): Enable processing multiple URLs at once.
        value (str): URL or space-separated URLs to load images from.
        fallback (any): Backup image to use if URL loading fails.

    Returns:
        tuple[list]: A list of processed images as torch tensors in BCHW format.

    Raises:
        ValueError: If URLs are invalid, images can't be loaded, or no input is provided.
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "subtype": (["image", "mask"], {"default": "image"}),
                "include_alpha": ("BOOLEAN", {"default": False}),
                "multiple": ("BOOLEAN", {"default": False}),
                "value": (
                    "STRING",
                    {
                        "default": "https://www.example.com/images/sample.jpg",
                        "multiline": True,
                    },
                ),
            },
            "optional": {
                "fallback": (any_type,),
            },
        }

    RETURN_TYPES = (any_type,)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    OUTPUT_IS_LIST = (True,)
    DESCRIPTION = """# Load Image From URL

    ## Overview
    Fetches and processes images from web URLs for your ComfyUI workflow.

    ## Features
    - Load images from any web URL (must start with "http")
    - Process single or multiple images
    - Convert to grayscale masks
    - Control transparency handling
    - Fallback option if loading fails

    ## Parameters
    - **Subtype**: Choose "image" for standard images or "mask" for grayscale masks
    - **Include Alpha**: When ON, preserves transparency; when OFF, removes it
    - **Multiple**: When ON, processes all space-separated URLs; when OFF, uses only the first
    - **Value**: Enter URL(s) of the images to load (separate multiple URLs with spaces)
    - **Fallback**: Optional backup image if URL loading fails

    ## Output
    - List of images in ComfyUI-compatible tensor format (BCHW)
    - Ready to connect to any image-processing node in ComfyUI

    Note: All images are automatically converted to the appropriate format based on your settings.
    """

    def execute(
        self,
        subtype: str = "image",
        include_alpha: bool = False,
        multiple: bool = False,
        value: str = "",
        fallback: Any = None,
    ) -> tuple[list[torch.Tensor]]:
        def post_process(output: TensorImage, include_alpha: bool) -> TensorImage:
            if output.shape[1] not in [3, 4]:
                if len(output.shape) == 2:  # (H,W)
                    output = TensorImage(output.unsqueeze(0).unsqueeze(0).expand(-1, 3, -1, -1))
                elif len(output.shape) == 3:  # (B,H,W)
                    output = TensorImage(output.unsqueeze(1).expand(-1, 3, -1, -1))
                elif len(output.shape) == 4 and output.shape[1] == 1:  # (B,1,H,W)
                    output = TensorImage(output.expand(-1, 3, -1, -1))
                else:
                    raise ValueError(f"Unsupported shape: {output.shape}")
            else:
                if not include_alpha and output.shape[1] == 4:
                    rgb = TensorImage(output[:, :3, :, :])
                    alpha = TensorImage(output[:, -1, :, :])
                    output, _ = cutout(rgb, alpha)
            return output

        def process_value(value: str, multiple: bool) -> list[str]:
            if not value:
                return []
            if " " in value:
                items = value.split(" ")
                return items if multiple else [items[0]]
            return [value]

        def load_image(url: str) -> Optional[TensorImage]:
            if not url:
                raise ValueError("Empty input string")

            try:
                if url.startswith("http"):
                    return TensorImage.from_web(url)
            except Exception as e:
                raise ValueError(f"Unsupported input format: {url}") from e

        value_list = process_value(value, multiple)
        outputs: list[torch.Tensor] = []

        # Process each input value
        for item in value_list:
            if isinstance(item, str):
                try:
                    output = load_image(item)
                    if output is not None:
                        outputs.append(output)
                except ValueError as e:
                    if not outputs:
                        raise e

        if len(outputs) == 0:
            if fallback is None:
                raise ValueError("No input found and no fallback provided")
            outputs.append(TensorImage.from_BWHC(fallback))

        for i, output in enumerate(outputs):
            if not isinstance(output, TensorImage):
                raise ValueError(f"Output {i} must be a TensorImage")

            if subtype == "mask":
                if output.shape[1] == 4:
                    rgb = TensorImage(output[:, :3, :, :])
                    outputs[i] = rgb_to_grayscale(rgb).get_BWHC()
                else:
                    outputs[i] = output.get_BWHC()
            else:
                outputs[i] = post_process(output, include_alpha).get_BWHC()
        return (outputs,)
