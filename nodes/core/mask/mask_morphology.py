import torch
from signature_core.functional.morphology import (
    bottom_hat,
    closing,
    dilation,
    erosion,
    gradient,
    opening,
    top_hat,
)
from signature_core.img.tensor_image import TensorImage

from .... import MAX_INT
from ...categories import MASK_CAT


class MaskMorphology:
    """Applies morphological operations to transform mask shapes and boundaries.

    Provides various morphological operations to modify mask shapes through kernel-based transformations.
    Supports multiple iterations for stronger effects.

    Args:
        mask (torch.Tensor): Input mask tensor in BWHC format
        operation (str): Morphological operation to apply. Options:
            - "dilation": Expands mask regions
            - "erosion": Shrinks mask regions
            - "opening": Erosion followed by dilation
            - "closing": Dilation followed by erosion
            - "gradient": Difference between dilation and erosion
            - "top_hat": Difference between input and opening
            - "bottom_hat": Difference between closing and input
        kernel_size (int): Size of the morphological kernel. Default: 1
        iterations (int): Number of times to apply the operation. Default: 5

    Returns:
        tuple[torch.Tensor]: A single-element tuple containing the processed mask in BWHC format

    Raises:
        ValueError: If mask is not a valid torch.Tensor or if operation is invalid

    Notes:
        - Larger kernel sizes and more iterations result in stronger morphological effects
        - Operations are performed using the TensorImage wrapper class for format consistency
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "operation": (
                    [
                        "dilation",
                        "erosion",
                        "opening",
                        "closing",
                        "gradient",
                        "top_hat",
                        "bottom_hat",
                    ],
                ),
                "kernel_size": (
                    "INT",
                    {"default": 1, "min": 1, "max": MAX_INT, "step": 2},
                ),
                "iterations": (
                    "INT",
                    {"default": 5, "min": 1, "max": MAX_INT, "step": 1},
                ),
            }
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "execute"
    CATEGORY = MASK_CAT
    DESCRIPTION = """
    Applies morphological operations to transform mask shapes and boundaries.
    Provides operations like dilation (expand), erosion (shrink), opening, closing, gradient, and more.
    Useful for refining mask edges and shapes.
    """

    def execute(
        self,
        mask: torch.Tensor,
        operation: str = "dilation",
        kernel_size: int = 1,
        iterations: int = 5,
    ) -> tuple[torch.Tensor]:
        step = TensorImage.from_BWHC(mask)

        operations = {
            "dilation": dilation,
            "erosion": erosion,
            "opening": opening,
            "closing": closing,
            "gradient": gradient,
            "top_hat": top_hat,
            "bottom_hat": bottom_hat,
        }

        if operation not in operations:
            raise ValueError(f"Invalid operation: {operation}")

        try:
            output = operations[operation](image=step, kernel_size=kernel_size, iterations=iterations)
        except KeyError:
            raise ValueError(f"Invalid operation: {operation}")

        return (output.get_BWHC(),)
