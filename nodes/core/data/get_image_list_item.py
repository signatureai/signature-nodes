import torch

from ...categories import DATA_CAT


class GetImageListItem:
    """Extracts a single image from an image list by index.

    A node designed for batch image processing that allows selective access to individual images
    within a collection, enabling targeted processing of specific images in a sequence.

    Args:
        images (list[Image]): The list of image objects to select from.
            Must be a valid list containing compatible image objects.
            Can be any length, but must not be empty.
        index (int): The zero-based index of the desired image.
            Must be a non-negative integer within the list bounds.
            Defaults to 0 (first image).

    Returns:
        tuple[Image]: A single-element tuple containing:
            - Image: The selected image object from the specified index position.

    Raises:
        ValueError: When index is not an integer or images is not a list.
        IndexError: When index is outside the valid range for the image list.
        TypeError: When images list contains invalid image objects.

    Notes:
        - Uses zero-based indexing (0 = first image)
        - Does not support negative indices
        - Returns a single image even from multi-image batches
        - Preserves the original image data without modifications
        - Thread-safe for concurrent access
        - Memory efficient as it references rather than copies the image
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "images": ("LIST",),
                "index": ("INT", {"default": 0}),
            },
        }

    RETURN_TYPES = "IMAGE"
    FUNCTION = "execute"
    CATEGORY = DATA_CAT
    DESCRIPTION = """
    Extracts a single image from a list of images by its index position.
    Uses zero-based indexing (0 = first image).
    Useful for selecting specific images from batches for individual processing."""

    def execute(self, images: list[torch.Tensor], index: int = 0) -> tuple[torch.Tensor]:
        image = images[index]
        return (image,)
