from typing import Optional

from signature_core.functional.augmentation import blur_augmentation

from ...categories import AUGMENTATION_CAT


class BlurAugmentation:
    """Applies various types of blur effects to images.

    This node provides multiple blur algorithms with configurable parameters for image
    softening effects.

    Args:
        blur_type (str): Type of blur to apply:
            - "gaussian": Gaussian blur
            - "motion": Motion blur
            - "median": Median filter blur
        blur_limit_min (int): Minimum blur kernel size (must be multiple of 3)
        blur_limit_max (int): Maximum blur kernel size (must be multiple of 3)
        percent (float): Probability of applying the blur (0.0-1.0)
        augmentation (AUGMENTATION, optional): Existing augmentation to chain with

    Returns:
        tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

    Notes:
        - Kernel size is randomly selected between min and max limits
        - Different blur types produce distinct softening effects
        - Larger kernel sizes create stronger blur effects
        - Can be chained with other augmentations
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "blur_type": (
                    ["gaussian", "motion", "median"],
                    {"default": "gaussian"},
                ),
                "blur_limit_min": ("INT", {"default": 3, "min": 3, "step": 3}),
                "blur_limit_max": ("INT", {"default": 87, "min": 3, "step": 3}),
                "percent": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                "augmentation": ("AUGMENTATION", {"default": None}),
            },
        }

    RETURN_TYPES = ("AUGMENTATION",)
    FUNCTION = "execute"
    CATEGORY = AUGMENTATION_CAT
    DESCRIPTION = """Adds blur effects to images with gaussian, motion, or median styles.
    Control blur strength and application frequency. Chain with other augmentations for creative transformations."""

    def execute(
        self,
        blur_type: str = "gaussian",
        blur_limit_min: int = 3,
        blur_limit_max: int = 87,
        percent: float = 0.3,
        augmentation: Optional[list] = None,
    ) -> tuple[list]:
        blur_limit = (blur_limit_min, blur_limit_max)
        augmentation = blur_augmentation(
            blur_type=blur_type,
            blur_limit=blur_limit,
            percent=percent,
            augmentation=augmentation,
        )
        return (augmentation,)
