from typing import Optional

from signature_core.functional.augmentation import flip_augmentation

from ...categories import AUGMENTATION_CAT


class FlipAugmentation:
    """Applies horizontal or vertical flip augmentation to images with configurable probability.

    This node performs random flip transformations on input images. It supports both horizontal and
    vertical flip operations with adjustable probability of application.

    Args:
        flip (str): Direction of flip operation, either:
            - "horizontal": Flips image left to right
            - "vertical": Flips image top to bottom
        percent (float): Probability of applying the flip, from 0.0 to 1.0.
        augmentation (AUGMENTATION, optional): Existing augmentation to chain with. Defaults to None.

    Returns:
        tuple: Contains a single element:
            augmentation (AUGMENTATION): The configured flip augmentation operation.

    Raises:
        ValueError: If flip direction is not "horizontal" or "vertical".
        ValueError: If percent is not between 0.0 and 1.0.

    Notes:
        - Flip direction cannot be changed after initialization
        - Setting percent to 0.5 applies the flip to approximately half of all samples
        - Can be chained with other augmentations through the augmentation parameter
        - Transformations are applied consistently when used with ComposeAugmentation
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "flip": (["horizontal", "vertical"], {"default": "horizontal"}),
                "percent": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                "augmentation": ("AUGMENTATION", {"default": None}),
            },
        }

    RETURN_TYPES = ("AUGMENTATION",)
    FUNCTION = "execute"
    CATEGORY = AUGMENTATION_CAT
    DESCRIPTION = "Applies horizontal or vertical flip transformations to images with adjustable probability. Creates mirror-image variations of your content. Chain with other augmentations for diverse image transformations."

    def execute(
        self,
        flip: str = "horizontal",
        percent: float = 0.5,
        augmentation: Optional[list] = None,
    ) -> tuple[list]:
        augmentation = flip_augmentation(flip, percent, augmentation)
        return (augmentation,)
