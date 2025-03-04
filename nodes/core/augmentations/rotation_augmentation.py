from typing import Optional

from signature_core.functional.augmentation import rotation_augmentation

from ...categories import AUGMENTATION_CAT


class RotationAugmentation:
    """Rotates images by random angles within specified limits.

    This node performs random rotation augmentation with configurable angle limits and
    application probability.

    Args:
        limit (int): Maximum rotation angle in degrees (0-180)
        percent (float): Probability of applying the rotation (0.0-1.0)
        augmentation (AUGMENTATION, optional): Existing augmentation to chain with

    Returns:
        tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

    Notes:
        - Rotation angles are randomly sampled between -limit and +limit
        - Empty areas after rotation are filled with black
        - Can be chained with other augmentations
        - Original aspect ratio is preserved
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "limit": ("INT", {"default": 45, "min": 0, "max": 180}),
                "percent": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                "augmentation": ("AUGMENTATION", {"default": None}),
            },
        }

    RETURN_TYPES = ("AUGMENTATION",)
    FUNCTION = "execute"
    CATEGORY = AUGMENTATION_CAT
    DESCRIPTION = """
    Rotates images by random angles within specified limits.
    Control rotation angle range and application frequency.
    Chain with other augmentations for diverse orientation variations."""

    def execute(
        self,
        limit: int = 45,
        percent: float = 0.5,
        augmentation: Optional[list] = None,
    ) -> tuple[list]:
        augmentation = rotation_augmentation(limit=limit, percent=percent, augmentation=augmentation)
        return (augmentation,)
