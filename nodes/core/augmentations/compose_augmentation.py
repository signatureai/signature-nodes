from typing import Optional

import torch
from signature_core.functional.augmentation import compose_augmentation
from signature_core.img.tensor_image import TensorImage

from ...categories import AUGMENTATION_CAT


class ComposeAugmentation:
    """Combines and applies multiple augmentation operations with consistent random transformations.

    This node orchestrates the application of multiple augmentation operations to images and masks. It
    provides control over sample generation and reproducibility through seed management.

    Args:
        augmentation (AUGMENTATION): The augmentation operation or chain to apply.
        samples (int): Number of augmented versions to generate. Must be >= 1.
        seed (int): Random seed for reproducible results. Use -1 for random seeding.
            Valid range: -1 to 10000000000000000.
        image (IMAGE, optional): Input image to augment. Defaults to None.
        mask (MASK, optional): Input mask to augment. Defaults to None.

    Returns:
        tuple: Contains two elements:
            images (List[IMAGE]): List of augmented versions of the input image.
            masks (List[MASK]): List of augmented versions of the input mask.

    Raises:
        ValueError: If neither image nor mask is provided.
        ValueError: If samples is less than 1.
        ValueError: If seed is outside valid range.

    Notes:
        - At least one of image or mask must be provided
        - All augmentations are applied consistently to both image and mask
        - Output is always returned as lists, even when samples=1
        - Using a fixed seed ensures reproducible augmentations
        - Supports chaining multiple augmentations through the augmentation parameter
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "augmentation": ("AUGMENTATION",),
                "samples": ("INT", {"default": 1, "min": 1}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 10000000000000000}),
            },
            "optional": {
                "image": ("IMAGE", {"default": None}),
                "mask": ("MASK", {"default": None}),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    FUNCTION = "execute"
    CATEGORY = AUGMENTATION_CAT
    OUTPUT_IS_LIST = (
        True,
        True,
    )
    DESCRIPTION = "Applies augmentations to images and masks, creating multiple variations with the same transformations. Control the number of samples and use seeds for reproducible results. Connect augmentation nodes to create complex transformation chains."

    def execute(
        self,
        augmentation: list,
        samples: int = 1,
        seed: int = -1,
        image: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
    ) -> tuple[list, list]:
        # Create a dummy image if only mask is provided
        if image is None and mask is not None:
            image = torch.zeros_like(mask)

        image_tensor = TensorImage.from_BWHC(image) if isinstance(image, torch.Tensor) else None
        mask_tensor = TensorImage.from_BWHC(mask) if isinstance(mask, torch.Tensor) else None

        total_images, total_masks = compose_augmentation(
            augmentation=augmentation,
            samples=samples,
            image_tensor=image_tensor,
            mask_tensor=mask_tensor,
            seed=seed,
        )

        if total_images is None:
            total_images = []
        if total_masks is None:
            total_masks = []
        node_image = [image.get_BWHC() for image in total_images]
        node_mask = [mask.get_BWHC() for mask in total_masks]

        return (
            node_image,
            node_mask,
        )
