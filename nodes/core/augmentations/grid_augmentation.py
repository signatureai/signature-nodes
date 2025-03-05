from typing import Optional

from signature_core.functional.augmentation import grid_augmentation

from ...categories import AUGMENTATION_CAT


class GridAugmentation:
    """Applies grid-based transformations to images.

    This node provides grid-based image modifications including shuffling and dropout
    effects.

    Args:
        grid_type (str): Type of grid transformation:
            - "shuffle": Randomly permute grid cells
            - "dropout": Randomly remove grid cells
        grid_size (int): Number of grid divisions (2-10)
        percent (float): Probability of applying the effect (0.0-1.0)
        augmentation (AUGMENTATION, optional): Existing augmentation to chain with

    Returns:
        tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

    Notes:
        - Image is divided into grid_size x grid_size cells
        - Shuffle randomly reorders grid cells
        - Dropout replaces cells with black
        - Can be chained with other augmentations
        - Maintains overall image structure while adding local variations
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "grid_type": (["shuffle", "dropout"], {"default": "shuffle"}),
                "grid_size": ("INT", {"default": 3, "min": 2, "max": 10}),
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
    Applies grid-based transformations to images with shuffle or dropout effects.
    Control grid size and application frequency. Maintains overall image structure while adding local variations.
    Chain with other augmentations for creative results."""

    def execute(
        self,
        grid_type: str = "shuffle",
        grid_size: int = 3,
        percent: float = 0.3,
        augmentation: Optional[list] = None,
    ) -> tuple[list]:
        augmentation = grid_augmentation(
            grid_type=grid_type,
            grid_size=grid_size,
            percent=percent,
            augmentation=augmentation,
        )
        return (augmentation,)
