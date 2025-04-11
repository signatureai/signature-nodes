import torch


class MaskArea:
    """
    A ComfyUI node that extracts information about white areas in a mask.

    This node analyzes a binary mask (where white pixels represent areas of interest)
    and calculates the percentage of white pixels and the absolute count of white pixels.

    Inputs:
        mask (torch.Tensor): A binary mask tensor where white pixels (values > 0.5)
                            represent areas of interest.

    Outputs:
        PERCENTAGE (float): The percentage of white pixels in the mask (0-100%).
        PIXELS (int): The absolute count of white pixels in the mask.

    Example:
        This node can be used to:
        - Measure the relative size of a masked region
        - Determine if a mask covers a significant portion of an image
        - Calculate the density of a mask for various image processing tasks
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("PERCENTAGE", "PIXELS")
    FUNCTION = "execute"
    CATEGORY = "mask"
    DESCRIPTION = "Extracts white areas from a mask"

    def execute(self, mask: torch.Tensor) -> tuple[float, int]:
        # Calculate total number of pixels
        total_pixels = mask.numel()

        # Count white pixels (pixels with value close to 1.0)
        # Using a threshold to account for floating point precision
        white_pixels = int(torch.sum(mask > 0.5).item())

        # Calculate percentage of white pixels
        white_percentage = (white_pixels / total_pixels) * 100.0 if total_pixels > 0 else 0.0

        return (white_percentage, white_pixels)
