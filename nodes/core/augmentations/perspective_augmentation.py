from typing import Optional

from signature_core.functional.augmentation import perspective_augmentation

from ...categories import AUGMENTATION_CAT


class PerspectiveAugmentation:
    """Applies perspective transformation effects to images.

    This node creates perspective distortion effects that simulate viewing angle changes,
    with configurable strength and probability.

    Args:
        scale (float): Strength of perspective effect (0.01-0.5)
        keep_size (bool): Whether to maintain original image size
        percent (float): Probability of applying the effect (0.0-1.0)
        augmentation (AUGMENTATION, optional): Existing augmentation to chain with

    Returns:
        tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

    Notes:
        - Scale controls the intensity of perspective change
        - keep_size=True maintains original dimensions
        - keep_size=False may change image size
        - Can be chained with other augmentations
        - Simulates realistic viewing angle variations
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scale": ("FLOAT", {"default": 0.05, "min": 0.01, "max": 0.5}),
                "keep_size": ("BOOLEAN", {"default": True}),
                "percent": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0}),
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
        scale: float = 0.05,
        keep_size: bool = True,
        percent: float = 0.3,
        augmentation: Optional[list] = None,
    ) -> tuple[list]:
        augmentation = perspective_augmentation(
            scale=scale, keep_size=keep_size, percent=percent, augmentation=augmentation
        )
        return (augmentation,)
