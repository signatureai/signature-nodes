from typing import Optional

import torch
from signature_core.functional.transform import rescale
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_PROCESSING_CAT


class Rescale:
    """Rescales images and masks by a specified factor while preserving aspect ratio.

    Provides flexible rescaling of images and masks with support for various interpolation
    methods and optional antialiasing. Useful for uniform scaling operations where
    maintaining aspect ratio is important.

    Args:
        image (torch.Tensor, optional): Input image in BWHC format with values in range [0, 1]
        mask (torch.Tensor, optional): Input mask in BWHC format with values in range [0, 1]
        factor (float): Scale multiplier (0.01-100.0)
        interpolation (str): Resampling method to use:
            - "nearest": Nearest neighbor (sharp, blocky)
            - "nearest-exact": Nearest neighbor without rounding
            - "bilinear": Linear interpolation (smooth)
            - "bicubic": Cubic interpolation (smoother)
            - "box": Box sampling (good for downscaling)
            - "hamming": Hamming windowed sampling
            - "lanczos": Lanczos resampling (sharp, fewer artifacts)
        antialias (bool): Whether to apply antialiasing when downscaling

    Returns:
        tuple:
            - image (torch.Tensor): Rescaled image in BWHC format
            - mask (torch.Tensor): Rescaled mask in BWHC format

    Raises:
        ValueError: If neither image nor mask is provided
        ValueError: If invalid interpolation method specified
        RuntimeError: If input tensors have invalid dimensions

    Notes:
        - At least one of image or mask must be provided
        - Output maintains the same number of channels as input
        - Antialiasing is recommended when downscaling to prevent artifacts
        - All interpolation methods preserve the value range [0, 1]
        - Memory usage scales quadratically with factor
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {},
            "optional": {
                "image": ("IMAGE", {"default": None}),
                "mask": ("MASK", {"default": None}),
                "factor": (
                    "FLOAT",
                    {"default": 2.0, "min": 0.01, "max": 100.0, "step": 0.01},
                ),
                "interpolation": (
                    [
                        "nearest",
                        "nearest-exact",
                        "bilinear",
                        "bicubic",
                        "box",
                        "hamming",
                        "lanczos",
                    ],
                ),
                "antialias": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT

    def execute(
        self,
        image: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        factor: float = 2.0,
        interpolation: str = "nearest",
        antialias: bool = True,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if not isinstance(image, torch.Tensor) and not isinstance(mask, torch.Tensor):
            raise ValueError("Either image or mask must be provided")
        input_image = (
            TensorImage.from_BWHC(image) if isinstance(image, torch.Tensor) else TensorImage(torch.zeros((1, 3, 1, 1)))
        )
        input_mask = (
            TensorImage.from_BWHC(mask) if isinstance(mask, torch.Tensor) else TensorImage(torch.zeros((1, 1, 1, 1)))
        )
        output_image = rescale(
            input_image,
            factor,
            interpolation,
            antialias,
        ).get_BWHC()
        output_mask = rescale(
            input_mask,
            factor,
            interpolation,
            antialias,
        ).get_BWHC()

        return (
            output_image,
            output_mask,
        )
