import torch

from ...categories import MASK_CAT


class GetMaskShape:
    """Analyzes and returns the dimensional information of a mask tensor.

    Extracts and returns the shape parameters of the input mask for analysis or debugging.

    Args:
        mask (torch.Tensor): Input mask in BWHC format

    Returns:
        tuple[int, int, int, int, str]: Tuple containing:
            - Batch size
            - Width
            - Height
            - Number of channels
            - String representation of shape

    Raises:
        ValueError: If mask is not a valid torch.Tensor

    Notes:
        - Handles both 3D and 4D tensor inputs
        - Useful for debugging and validation
        - Returns dimensions in a consistent order regardless of input format
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
            },
        }

    RETURN_TYPES = ("INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("batch", "width", "height", "channels", "debug")
    FUNCTION = "execute"
    CATEGORY = MASK_CAT
    DESCRIPTION = "Analyzes and returns the dimensional information of a mask tensor. Extracts shape parameters (batch size, width, height, channels) for analysis or debugging. Handles both 3D and 4D tensor inputs."

    def execute(self, mask: torch.Tensor) -> tuple[int, int, int, int, str]:
        if len(mask.shape) == 3:
            return (mask.shape[0], mask.shape[2], mask.shape[1], 1, str(mask.shape))
        return (
            mask.shape[0],
            mask.shape[2],
            mask.shape[1],
            mask.shape[3],
            str(mask.shape),
        )
