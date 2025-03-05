import torch

from ...categories import IMAGE_CAT


class ImageBatch2List:
    """Splits a batched tensor of images into individual images.

    Converts a batch of images stored in a single tensor into a list of separate image tensors,
    useful for processing images individually after batch operations.

    Args:
        image (torch.Tensor): Batched input images in BWHC format

    Returns:
        tuple[list[torch.Tensor]]: Single-element tuple containing:
            - list: Individual images, each in BWHC format with batch size 1

    Raises:
        ValueError: If image is not a torch.Tensor

    Notes:
        - Each output image maintains original dimensions and channels
        - Output images have batch dimension of 1
        - Useful for post-processing individual images after batch operations
        - Memory efficient as it uses views when possible
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",)}}

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    CLASS_ID = "image_batch_list"
    OUTPUT_IS_LIST = (True,)
    DESCRIPTION = """
    Splits a batched tensor of images into a list of individual images.
    Converts a single tensor containing multiple images into separate tensors, each with batch size 1.
    Useful for processing images individually after batch operations.
    """

    def execute(self, image: torch.Tensor) -> tuple[list[torch.Tensor]]:
        image_list = [img.unsqueeze(0) for img in image]
        return (image_list,)
