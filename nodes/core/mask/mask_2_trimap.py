import torch
from signature_core.functional.morphology import dilation, erosion
from signature_core.img.tensor_image import TensorImage

from ...categories import MASK_CAT


class Mask2Trimap:
    """Converts a binary mask into a trimap representation with three distinct regions.

    Creates a trimap by identifying definite foreground, definite background, and uncertain regions
    using threshold values and morphological operations.

    Args:
        mask (torch.Tensor): Input binary mask in BWHC format
        inner_min_threshold (int): Minimum threshold for inner/foreground region. Default: 200
        inner_max_threshold (int): Maximum threshold for inner/foreground region. Default: 255
        outer_min_threshold (int): Minimum threshold for outer/background region. Default: 15
        outer_max_threshold (int): Maximum threshold for outer/background region. Default: 240
        kernel_size (int): Size of morphological kernel for region processing. Default: 10

    Returns:
        tuple[torch.Tensor, torch.Tensor]: Tuple containing:
            - Processed mask in BWHC format
            - Trimap tensor with foreground, background, and uncertain regions

    Raises:
        ValueError: If mask is not a valid torch.Tensor

    Notes:
        - Output trimap has values: 0 (background), 0.5 (uncertain), 1 (foreground)
        - Kernel size affects the smoothness of region boundaries
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "inner_min_threshold": ("INT", {"default": 200, "min": 0, "max": 255}),
                "inner_max_threshold": ("INT", {"default": 255, "min": 0, "max": 255}),
                "outer_min_threshold": ("INT", {"default": 15, "min": 0, "max": 255}),
                "outer_max_threshold": ("INT", {"default": 240, "min": 0, "max": 255}),
                "kernel_size": ("INT", {"default": 10, "min": 1, "max": 100}),
            }
        }

    RETURN_TYPES = ("MASK", "TRIMAP")
    FUNCTION = "execute"
    CATEGORY = MASK_CAT
    CLASS_ID = "mask_trimap"
    DESCRIPTION = "Converts a binary mask into a trimap representation with three distinct regions. Creates a trimap by identifying definite foreground, definite background, and uncertain regions using thresholds and morphological operations."

    def execute(
        self,
        mask: torch.Tensor,
        inner_min_threshold: int = 200,
        inner_max_threshold: int = 255,
        outer_min_threshold: int = 15,
        outer_max_threshold: int = 240,
        kernel_size: int = 10,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        step = TensorImage.from_BWHC(mask)
        inner_mask = TensorImage(step.clone())
        inner_mask[inner_mask > (inner_max_threshold / 255.0)] = 1.0
        inner_mask[inner_mask <= (inner_min_threshold / 255.0)] = 0.0

        step = TensorImage.from_BWHC(mask)
        inner_mask = erosion(image=inner_mask, kernel_size=kernel_size, iterations=1)

        inner_mask[inner_mask != 0.0] = 1.0

        outter_mask = step.clone()
        outter_mask[outter_mask > (outer_max_threshold / 255.0)] = 1.0
        outter_mask[outter_mask <= (outer_min_threshold / 255.0)] = 0.0
        outter_mask = dilation(image=inner_mask, kernel_size=kernel_size, iterations=5)

        outter_mask[outter_mask != 0.0] = 1.0

        trimap_im = torch.zeros_like(step)
        trimap_im[outter_mask == 1.0] = 0.5
        trimap_im[inner_mask == 1.0] = 1.0
        batch_size = step.shape[0]

        trimap = torch.zeros(
            batch_size,
            2,
            step.shape[2],
            step.shape[3],
            dtype=step.dtype,
            device=step.device,
        )
        for i in range(batch_size):
            tar_trimap = trimap_im[i][0]
            trimap[i][1][tar_trimap == 1] = 1
            trimap[i][0][tar_trimap == 0] = 1

        output_0 = TensorImage(trimap_im).get_BWHC()
        output_1 = trimap.permute(0, 2, 3, 1)

        return (
            output_0,
            output_1,
        )
