from typing import Optional

from signature_core.functional.augmentation import shift_scale_augmentation

from ...categories import AUGMENTATION_CAT


class ShiftScaleAugmentation:
    """Applies random shifting, scaling, and rotation transformations.

    This node combines multiple geometric transformations with configurable ranges
    and probability.

    Args:
        shift_limit (float): Maximum shift as fraction of image size (0.0-1.0)
        scale_limit (float): Maximum scale factor change (0.0-1.0)
        rotate_limit (int): Maximum rotation angle in degrees (0-180)
        percent (float): Probability of applying transformations (0.0-1.0)
        augmentation (AUGMENTATION, optional): Existing augmentation to chain with

    Returns:
        tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

    Notes:
        - Shift moves image content within frame
        - Scale changes overall image size
        - Rotation angles are randomly sampled
        - Can be chained with other augmentations
        - All transformations are applied together when selected
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "shift_limit": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0}),
                "scale_limit": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0}),
                "rotate_limit": ("INT", {"default": 45, "min": 0, "max": 180}),
                "percent": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                "augmentation": ("AUGMENTATION", {"default": None}),
            },
        }

    RETURN_TYPES = ("AUGMENTATION",)
    FUNCTION = "execute"
    CATEGORY = AUGMENTATION_CAT
    DESCRIPTION = """
    Applies random shifting, scaling, and rotation transformations to images.
    Control transformation ranges and application frequency.
    Chain with other augmentations for diverse geometric variations."""

    def execute(
        self,
        shift_limit: float = 0.1,
        scale_limit: float = 0.2,
        rotate_limit: int = 45,
        percent: float = 0.3,
        augmentation: Optional[list] = None,
    ) -> tuple[list]:
        augmentation = shift_scale_augmentation(
            shift_limit=shift_limit,
            scale_limit=scale_limit,
            rotate_limit=rotate_limit,
            percent=percent,
            augmentation=augmentation,
        )
        return (augmentation,)
