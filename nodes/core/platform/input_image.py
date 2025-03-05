from typing import Any, Optional

import torch
from signature_core.functional.transform import cutout
from signature_core.img.tensor_image import TensorImage

from ...categories import PLATFORM_IO_CAT
from ...shared import any_type


class InputImage:
    """Processes and validates image inputs from various sources for the platform.

    This class handles image input processing, supporting both single and multiple images from URLs. It includes
    functionality for alpha channel management and mask generation.

    Args:
        title (str): Display title for the input node. Defaults to "Input Image".
        subtype (str): Type of input - either "image" or "mask".
        required (bool): Whether the input is required. Defaults to True.
        include_alpha (bool): Whether to preserve alpha channel. Defaults to False.
        multiple (bool): Allow multiple image inputs. Defaults to False.
        value (str): Image data as URL.
        metadata (str): JSON string containing additional metadata. Defaults to "{}".
        fallback (any): Optional fallback value if no input is provided.

    Returns:
        tuple[list]: A tuple containing a list of processed images as torch tensors in BWHC format.

    Raises:
        ValueError: If value is not a string, subtype is invalid, or no valid input is found.

    Notes:
        - URLs must start with "http" to be recognized
        - Multiple images can be provided as comma-separated values
        - Alpha channels are removed by default unless include_alpha is True
        - Mask inputs are automatically converted to grayscale
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "title": ("STRING", {"default": "Input Image"}),
                "subtype": (["image", "mask"], {"default": "image"}),
                "required": ("BOOLEAN", {"default": True}),
                "include_alpha": ("BOOLEAN", {"default": False}),
                "multiple": ("BOOLEAN", {"default": False}),
                "value": (
                    "STRING",
                    {
                        "default": "https://www.example.com/images/sample.jpg",
                        "multiline": True,
                    },
                ),
                "metadata": ("STRING", {"default": "{}", "multiline": True}),
            },
            "optional": {
                "fallback": (any_type,),
            },
        }

    RETURN_TYPES = (any_type,)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT
    OUTPUT_IS_LIST = (True,)
    DESCRIPTION = """# InputImage Node - Your Gateway for Images in ComfyUI

    ## What it Does 🎨
    This node is your main entry point for bringing images into ComfyUI workflows. Think of it as a universal image
    loader that can handle:
    - Images from web URLs (anything starting with "http")
    - Single images or multiple images at once
    - Regular images and masks
    - Images with or without transparency

    ## How to Use It 🚀

    ### Basic Settings
    - **Title**: Just a label for your node (default: "Input Image")
    - **Subtype**: Choose between:
        - `image` - for regular images
        - `mask` - for masks (automatically converts to grayscale)
    - **Include Alpha**: Toggle transparency handling
        - OFF: Removes transparency (default)
        - ON: Keeps transparency channel
    - **Multiple**: Allow multiple images
        - OFF: Takes only first image (default)
        - ON: Processes all provided images

    ### Input Methods
    1. Web Images: Just paste the image URL (must start with "http")
    2. Multiple Images: With "Multiple" enabled, separate URLs with spaces
    3. Fallback: Optional backup image if main input fails

    ## Tips & Tricks 💡
    - For batch processing, enable "Multiple" and input several URLs separated by spaces
    - When working with masks, set "subtype" to "mask" for automatic grayscale conversion
    - If you need transparency in your workflow, make sure to enable "Include Alpha"
    - The node automatically handles various image formats and color spaces

    ## Output
    - Outputs images in the format ComfyUI expects (BCHW tensor format)
    - Perfect for feeding into other ComfyUI nodes like upscalers, ControlNet, or image processors

    Think of this node as your universal image importer - it handles all the technical conversion stuff so you can focus
    on the creative aspects of your workflow! 🎨✨"""

    def execute(
        self,
        title: str = "Input Image",
        subtype: str = "image",
        required: bool = True,
        include_alpha: bool = False,
        multiple: bool = False,
        value: str = "",
        metadata: str = "{}",
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
                outputs[i] = output.get_grayscale().get_BWHC()
            else:
                outputs[i] = post_process(output, include_alpha).get_BWHC()
        return (outputs,)
