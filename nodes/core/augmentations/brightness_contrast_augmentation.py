from typing import Optional

from signature_core.functional.augmentation import brightness_contrast_augmentation

from ...categories import AUGMENTATION_CAT


class BrightnessContrastAugmentation:
    """Applies brightness and contrast adjustments to images.

    This node provides controls for adjusting image brightness and contrast with configurable
    limits and probability of application.

    Args:
        brightness_limit (float): Maximum brightness adjustment range (0.0-1.0)
        contrast_limit (float): Maximum contrast adjustment range (0.0-1.0)
        percent (float): Probability of applying the augmentation (0.0-1.0)
        augmentation (AUGMENTATION, optional): Existing augmentation to chain with

    Returns:
        tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

    Notes:
        - Brightness adjustments are applied as multiplicative factors
        - Contrast adjustments modify image histogram spread
        - Can be chained with other augmentations
        - Actual adjustment values are randomly sampled within limits
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "brightness_limit": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0}),
                "contrast_limit": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0}),
                "percent": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                "augmentation": ("AUGMENTATION", {"default": None}),
            },
        }

    RETURN_TYPES = ("AUGMENTATION",)
    FUNCTION = "execute"
    CATEGORY = AUGMENTATION_CAT
    DESCRIPTION = """Adjusts image brightness and contrast during generation.
    Control modification ranges and application frequency.
    Chain with other augmentations for creative image variations."""

    def execute(
        self,
        brightness_limit: float = 0.2,
        contrast_limit: float = 0.2,
        percent: float = 0.5,
        augmentation: Optional[list] = None,
    ) -> tuple[list]:
        augmentation = brightness_contrast_augmentation(
            brightness_limit=brightness_limit,
            contrast_limit=contrast_limit,
            percent=percent,
            augmentation=augmentation,
        )
        return (augmentation,)
