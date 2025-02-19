from typing import Optional

from signature_core.functional.augmentation import cutout_augmentation

from ...categories import AUGMENTATION_CAT


class CutoutAugmentation:
    """Creates random rectangular cutouts in images.

    This node randomly removes rectangular regions from images by filling them with black,
    useful for regularization and robustness training.

    Args:
        num_holes (int): Number of cutout regions to create (1-20)
        max_size (int): Maximum size of cutout regions in pixels (1-100)
        percent (float): Probability of applying cutouts (0.0-1.0)
        augmentation (AUGMENTATION, optional): Existing augmentation to chain with

    Returns:
        tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

    Notes:
        - Cutout positions are randomly selected
        - Each cutout region is independently sized
        - Regions are filled with black (zero) values
        - Can be chained with other augmentations
        - Useful for preventing overfitting
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "num_holes": ("INT", {"default": 8, "min": 1, "max": 20}),
                "max_size": ("INT", {"default": 30, "min": 1, "max": 100}),
                "percent": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                "min_num_holes": ("INT", {"default": 1, "min": 1, "max": 20}),
                "min_size": ("INT", {"default": 1, "min": 1, "max": 100}),
                "augmentation": ("AUGMENTATION", {"default": None}),
            },
        }

    RETURN_TYPES = ("AUGMENTATION",)
    FUNCTION = "execute"
    CATEGORY = AUGMENTATION_CAT

    def execute(
        self,
        num_holes: int = 8,
        max_size: int = 30,
        percent: float = 0.3,
        min_num_holes: int = 1,
        min_size: int = 1,
        augmentation: Optional[list] = None,
    ) -> tuple[list]:
        augmentation = cutout_augmentation(
            num_holes=num_holes,
            max_size=max_size,
            percent=percent,
            min_num_holes=min_num_holes,
            min_size=min_size,
            augmentation=augmentation,
        )
        return (augmentation,)
