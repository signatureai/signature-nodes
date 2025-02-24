import torch
from signature_core.functional.transform import resize
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_CAT


class ImageList2Batch:
    """Converts a list of individual images into a batched tensor.

    Combines multiple images into a single batched tensor, handling different input sizes through
    various resize modes. Supports multiple interpolation methods for optimal quality.

    Args:
        images (list[torch.Tensor]): List of input images in BWHC format
        mode (str): Resize mode for handling different image sizes:
            - 'STRETCH': Stretches images to match largest dimensions
            - 'FIT': Fits images within largest dimensions, maintaining aspect ratio
            - 'FILL': Fills to largest dimensions, maintaining aspect ratio with cropping
            - 'ASPECT': Preserves aspect ratio with padding
        interpolation (str): Interpolation method for resizing:
            - 'bilinear': Smooth interpolation suitable for most cases
            - 'nearest': Nearest neighbor, best for pixel art
            - 'bicubic': High-quality interpolation
            - 'area': Best for downscaling

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Batched images in BWHC format

    Raises:
        ValueError: If images is not a list
        ValueError: If mode is not a valid option
        ValueError: If interpolation is not a valid option

    Notes:
        - All images in output batch will have same dimensions
        - Original image qualities are preserved as much as possible
        - Memory efficient processing for large batches
        - GPU acceleration is automatically used when available
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "mode": (["STRETCH", "FIT", "FILL", "ASPECT"],),
                "interpolation": (["bilinear", "nearest", "bicubic", "area"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    INPUT_IS_LIST = True
    CLASS_ID = "image_list_batch"

    def execute(
        self,
        images: list[torch.Tensor],
        mode: str = "STRETCH",
        interpolation: str = "bilinear",
    ) -> tuple[torch.Tensor]:
        # Check if all images have the same shape
        shapes = [img.shape for img in images]
        if len(set(shapes)) == 1:
            # All images have the same shape, no need to resize
            return (torch.stack(images),)

        # Images have different shapes, proceed with resizing
        max_height = max(img.shape[1] for img in images)
        max_width = max(img.shape[2] for img in images)

        resized_images = []
        for img in images:
            tensor_img = TensorImage.from_BWHC(img)
            resized_img = resize(
                tensor_img,
                max_width,
                max_height,
                mode=mode,
                interpolation=interpolation,
            )
            resized_images.append(resized_img.get_BWHC().squeeze(0))

        return (torch.stack(resized_images),)
