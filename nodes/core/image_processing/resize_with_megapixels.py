import math
from typing import Optional

import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_PROCESSING_CAT
from .resize import Resize


class ResizeWithMegapixels:
    """Resizes images and masks to a target megapixel count while preserving aspect ratio.

    A specialized resizing node that targets a specific image size in megapixels rather than
    exact dimensions. This is useful for batch processing images to a consistent size while
    maintaining their original proportions and managing memory usage.

    Args:
        megapixels (float): Target size in megapixels (0.01-100.0)
        image (torch.Tensor, optional): Input image in BWHC format with values in range [0, 1]
        mask (torch.Tensor, optional): Input mask in BWHC format with values in range [0, 1]
        interpolation (str): Resampling method:
            - "bilinear": Linear interpolation (smooth)
            - "nearest": Nearest neighbor (sharp)
            - "bicubic": Cubic interpolation (smoother)
            - "area": Area averaging (good for downscaling)
        antialias (bool): Whether to apply antialiasing when downscaling

    Returns:
        tuple:
            - image (torch.Tensor): Resized image in BWHC format
            - mask (torch.Tensor): Resized mask in BWHC format

    Raises:
        ValueError: If neither image nor mask is provided
        ValueError: If invalid interpolation method
        RuntimeError: If input tensors have invalid dimensions

    Notes:
        - At least one of image or mask must be provided
        - Output maintains the same number of channels as input
        - Aspect ratio is always preserved
        - Target dimensions are calculated as sqrt(megapixels * 1M * aspect_ratio)
        - Actual output size may vary slightly due to rounding
        - Memory usage scales linearly with megapixel count
        - Antialiasing recommended when downscaling
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "megapixels": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.01, "max": 100.0, "step": 0.1},
                ),
            },
            "optional": {
                "image": ("IMAGE", {"default": None}),
                "mask": ("MASK", {"default": None}),
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
    DESCRIPTION = """Resize images based on total pixel count (megapixels) while keeping proportions.

    Instead of specifying exact width and height, this node lets you target a specific image size in megapixels. For
    example:
    - 1 megapixel = 1000x1000 pixels for a square image
    - 0.5 megapixels = roughly 707x707 pixels
    - 2 megapixels = roughly 1414x1414 pixels

    This is useful when you want to:
    - Resize a batch of images to a consistent size/quality level
    - Reduce memory usage by targeting a specific megapixel count
    - Maintain image proportions while hitting a target file size
    - Prepare images for specific platforms with megapixel limits

    The image will keep its original proportions - a wide image will stay wide, just with the total pixel count you
    specify."""

    def get_dimensions(self, megapixels: float, original_width: int = 0, original_height: int = 0) -> tuple[int, int]:
        """Calculate target dimensions based on megapixels while preserving aspect ratio.

        Args:
            megapixels (float): Target size in megapixels
            original_width (int): Original image width (optional)
            original_height (int): Original image height (optional)

        Returns:
            tuple[int, int]: Target (width, height)
        """
        total_pixels = megapixels * 1000000

        if original_width > 0 and original_height > 0:
            # Preserve aspect ratio if original dimensions are provided
            aspect_ratio = original_width / original_height
            height = math.sqrt(total_pixels / aspect_ratio)
            width = height * aspect_ratio
        else:
            # Default to square dimensions if no original dimensions
            width = height = math.sqrt(total_pixels)

        return (round(width), round(height))

    def execute(
        self,
        megapixels: float = 1.0,
        image: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        interpolation: str = "lanczos",
        antialias: bool = True,
        multiple_of: int = 1,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if isinstance(image, torch.Tensor):
            shape = TensorImage.from_BWHC(image).shape

        elif isinstance(mask, torch.Tensor):
            shape = TensorImage.from_BWHC(mask).shape

        else:
            raise ValueError("Either image or mask must be provided")

        _, _, orig_height, orig_width = shape

        target_width, target_height = self.get_dimensions(megapixels, orig_width, orig_height)

        # Create a Resize instance and call its execute method
        resize_node = Resize()
        output_image, output_mask = resize_node.execute(
            image=image,
            mask=mask,
            width=target_width,
            height=target_height,
            mode="ASPECT",
            interpolation=interpolation,
            antialias=antialias,
            multiple_of=multiple_of,
        )

        return (output_image, output_mask)
