from typing import Optional

import torch
from signature_core.functional.transform import resize
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_PROCESSING_CAT


class Resize:
    """Resizes images and masks to specific dimensions with multiple sizing modes.

    A versatile resizing node that supports multiple modes for handling aspect ratio
    and provides fine control over interpolation methods. Suitable for preparing
    images for specific size requirements while maintaining quality.

    Args:
        image (torch.Tensor, optional): Input image in BWHC format with values in range [0, 1]
        mask (torch.Tensor, optional): Input mask in BWHC format with values in range [0, 1]
        width (int): Target width in pixels (32-40960)
        height (int): Target height in pixels (32-40960)
        mode (str): How to handle aspect ratio:
            - "STRETCH": Force to exact dimensions, may distort
            - "FIT": Fit within dimensions, may be smaller
            - "FILL": Fill dimensions, may crop
            - "ASPECT": Preserve aspect ratio, fit longest side
        interpolation (str): Resampling method:
            - "bilinear": Linear interpolation (smooth)
            - "nearest": Nearest neighbor (sharp)
            - "bicubic": Cubic interpolation (smoother)
            - "area": Area averaging (good for downscaling)
        antialias (bool): Whether to apply antialiasing when downscaling
        multiple_of (int, optional): Ensure output dimensions are multiples of this value.
            If provided, final dimensions will be adjusted to nearest multiple.

    Returns:
        tuple:
            - image (torch.Tensor): Resized image in BWHC format
            - mask (torch.Tensor): Resized mask in BWHC format

    Raises:
        ValueError: If neither image nor mask is provided
        ValueError: If dimensions are out of valid range
        ValueError: If invalid mode or interpolation method
        RuntimeError: If input tensors have invalid dimensions

    Notes:
        - At least one of image or mask must be provided
        - Output maintains the same number of channels as input
        - STRETCH mode may distort image proportions
        - FIT mode ensures no cropping but may not fill target size
        - FILL mode ensures target size but may crop content
        - ASPECT mode preserves proportions using longest edge
        - Antialiasing recommended when downscaling
        - When multiple_of is set, final dimensions will be adjusted to nearest multiple
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {},
            "optional": {
                "image": ("IMAGE", {"default": None}),
                "mask": ("MASK", {"default": None}),
                "width": ("INT", {"default": 1024, "min": 32, "step": 2, "max": 40960}),
                "height": (
                    "INT",
                    {"default": 1024, "min": 32, "step": 2, "max": 40960},
                ),
                "mode": (["STRETCH", "FIT", "FILL", "ASPECT"],),
                "interpolation": (["lanczos", "bilinear", "nearest", "bicubic", "area"],),
                "antialias": (
                    "BOOLEAN",
                    {"default": True},
                ),
                "multiple_of": (
                    "INT",
                    {"default": 1, "min": 1, "step": 1, "max": 1024},
                ),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT
    DESCRIPTION = """🖼️ Image Resize Node

    This node helps you resize your images and masks to specific dimensions.
    Think of it like adjusting your canvas size,but with some smart options!

    What it does:
    - Resizes images as well as masks to any size you want (between 32 and 40,960 pixels)
    - Gives you different ways to handle the resizing

    Resize Modes:
    - STRETCH: Like stretching a rubber image to fit exactly (might distort)
    - FIT: Like putting a photo in a frame while keeping everything visible (might leave empty space)
    - FILL: Like zooming until the frame is completely filled (might crop edges)
    - ASPECT: Keeps everything looking natural by maintaining proportions

    Pro Tips:
    - Use "lanczos" for the highest quality resizing (especially good for photos and detailed art)
    - Use "bilinear" or "bicubic" for smooth, natural-looking results
    - Use "nearest" if you want to keep sharp edges (good for pixel art or masks)
    - Turn on "antialias" when making images smaller to avoid jagged edges
    - Use "multiple_of" if you need dimensions to be divisible by a certain number
    (useful for some AI models that require specific sizes)

    Perfect for:
    - Preparing images for AI models
    - Standardizing image sizes in your workflow
    - Resizing while keeping image quality
    - Making sure your images fit specific size requirements
    """

    def execute(
        self,
        image: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        width: int = 1024,
        height: int = 1024,
        mode: str = "default",
        interpolation: str = "lanczos",
        antialias: bool = True,
        multiple_of: int = 1,
    ):
        input_image = (
            TensorImage.from_BWHC(image)
            if isinstance(image, torch.Tensor)
            else TensorImage(torch.zeros((1, 3, width, height)))
        )
        input_mask = (
            TensorImage.from_BWHC(mask)
            if isinstance(mask, torch.Tensor)
            else TensorImage(torch.zeros((1, 1, width, height)))
        )

        output_image = resize(input_image, width, height, mode, interpolation, antialias, multiple_of).get_BWHC()
        output_mask = resize(input_mask, width, height, mode, interpolation, antialias, multiple_of).get_BWHC()

        return (
            output_image,
            output_mask,
        )
