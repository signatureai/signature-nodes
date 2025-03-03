from signature_core.functional.augmentation import random_crop_augmentation

from ...categories import AUGMENTATION_CAT


class RandomCropAugmentation:
    """Applies random crop augmentation to images with configurable dimensions and frequency.

    This node performs random cropping operations on input images. It allows precise control over the
    crop dimensions through minimum and maximum window sizes, target dimensions, and application
    probability.

    Args:
        height (int): Target height for the crop operation. Must be at least 32 and a multiple of 32.
        width (int): Target width for the crop operation. Must be at least 32 and a multiple of 32.
        min_window (int): Minimum size of the crop window. Must be a multiple of 32.
        max_window (int): Maximum size of the crop window. Must be a multiple of 32.
        percent (float): Probability of applying the crop, from 0.0 to 1.0.
        augmentation (AUGMENTATION, optional): Existing augmentation to chain with. Defaults to None.

    Returns:
        tuple: Contains a single element:
            augmentation (AUGMENTATION): The configured crop augmentation operation.

    Raises:
        ValueError: If any dimension parameters are not multiples of 32.
        ValueError: If min_window is larger than max_window.
        ValueError: If percent is not between 0.0 and 1.0.

    Notes:
        - Window size is randomly selected between min_window and max_window for each operation
        - Can be chained with other augmentations through the augmentation parameter
        - All dimension parameters must be multiples of 32 for proper operation
        - Setting percent to 1.0 ensures the crop is always applied
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "height": ("INT", {"default": 1024, "min": 32, "step": 32}),
                "width": ("INT", {"default": 1024, "min": 32, "step": 32}),
                "min_window": ("INT", {"default": 256, "step": 32}),
                "max_window": ("INT", {"default": 1024, "step": 32}),
                "percent": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                "augmentation": ("AUGMENTATION", {"default": None}),
            },
        }

    RETURN_TYPES = ("AUGMENTATION",)
    FUNCTION = "execute"
    CATEGORY = AUGMENTATION_CAT
    DESCRIPTION = "Performs random cropping on images with configurable dimensions and frequency. Control crop window size range and target output dimensions. Chain with other augmentations for diverse composition variations."

    def execute(
        self,
        height: int = 1024,
        width: int = 1024,
        min_window: int = 256,
        max_window: int = 1024,
        percent: float = 1.0,
        augmentation: list | None = None,
    ) -> tuple[list]:
        augmentation = random_crop_augmentation(
            height, width, min_window, max_window, percent, augmentation
        )

        return (augmentation,)
