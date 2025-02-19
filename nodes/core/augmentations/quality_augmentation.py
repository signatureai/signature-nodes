from typing import Optional

from signature_core.functional.augmentation import quality_augmentation

from ...categories import AUGMENTATION_CAT


class QualityAugmentation:
    """Simulates image quality degradation through compression or downscaling.

    This node provides options to reduce image quality in ways that simulate real-world
    quality loss scenarios.

    Args:
        quality_type (str): Type of quality reduction:
            - "compression": JPEG-like compression artifacts
            - "downscale": Resolution reduction and upscaling
        quality_limit (int): Quality parameter (1-100, lower = more degradation)
        percent (float): Probability of applying the effect (0.0-1.0)
        augmentation (AUGMENTATION, optional): Existing augmentation to chain with

    Returns:
        tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

    Notes:
        - Compression type simulates JPEG artifacts
        - Downscale type reduces and restores resolution
        - Lower quality limits produce more visible artifacts
        - Can be chained with other augmentations
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "quality_type": (
                    ["compression", "downscale"],
                    {"default": "compression"},
                ),
                "quality_limit": ("INT", {"default": 60, "min": 1, "max": 100}),
                "percent": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                "augmentation": ("AUGMENTATION", {"default": None}),
            },
        }

    RETURN_TYPES = ("AUGMENTATION",)
    FUNCTION = "execute"
    CATEGORY = AUGMENTATION_CAT

    def execute(
        self,
        quality_type: str = "compression",
        quality_limit: int = 60,
        percent: float = 0.2,
        augmentation: Optional[list] = None,
    ) -> tuple[list]:
        augmentation = quality_augmentation(
            quality_type=quality_type,
            quality_limit=quality_limit,
            percent=percent,
            augmentation=augmentation,
        )
        return (augmentation,)
