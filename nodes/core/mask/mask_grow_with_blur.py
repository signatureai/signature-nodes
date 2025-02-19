import torch
from kornia import filters, morphology
from signature_core.img.tensor_image import TensorImage

from .... import MAX_INT
from ...categories import MASK_CAT


class MaskGrowWithBlur:
    """Expands or contracts a mask with controllable blur and tapering effects.

    Provides fine control over mask growth with options for smooth transitions and edge effects.

    Args:
        mask (torch.Tensor): Input mask in BWHC format
        expand (int): Pixels to grow (positive) or shrink (negative). Default: 0
        incremental_expandrate (float): Growth rate per iteration. Default: 0.0
        tapered_corners (bool): Enable corner softening. Default: True
        flip_input (bool): Invert input before processing. Default: False
        blur_radius (float): Final blur amount. Default: 0.0
        lerp_alpha (float): Blend factor for transitions. Default: 1.0
        decay_factor (float): Growth decay rate. Default: 1.0

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing the processed mask

    Raises:
        ValueError: If inputs are invalid types or values

    Notes:
        - Positive expand values grow the mask, negative values shrink it
        - Decay factor controls how growth diminishes over iterations
        - Blur radius affects the final edge smoothness
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "expand": (
                    "INT",
                    {
                        "default": 0,
                        "min": -MAX_INT,
                        "max": MAX_INT,
                        "step": 1,
                    },
                ),
                "incremental_expandrate": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.1},
                ),
                "tapered_corners": ("BOOLEAN", {"default": True}),
                "flip_input": ("BOOLEAN", {"default": False}),
                "blur_radius": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 100, "step": 0.1},
                ),
                "lerp_alpha": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "decay_factor": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            },
        }

    CATEGORY = MASK_CAT
    RETURN_TYPES = ("MASK", "MASK")
    RETURN_NAMES = ("mask", "inverted mask")
    FUNCTION = "expand_mask"

    def expand_mask(
        self,
        mask: torch.Tensor,
        expand: int = 0,
        incremental_expandrate: float = 0.0,
        tapered_corners: bool = True,
        flip_input: bool = False,
        blur_radius: float = 0.0,
        lerp_alpha: float = 1.0,
        decay_factor: float = 1.0,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        mask = TensorImage.from_BWHC(mask)
        alpha = lerp_alpha
        decay = decay_factor
        if flip_input:
            mask = 1.0 - mask
        c = 0 if tapered_corners else 1
        kernel = torch.tensor([[c, 1, c], [1, 1, 1], [c, 1, c]], dtype=torch.float32)
        growmask = mask.reshape((-1, mask.shape[-2], mask.shape[-1])).cpu()
        out = []
        previous_output = None
        current_expand = expand
        for m in growmask:
            m = m.unsqueeze(0).unsqueeze(0)
            output = m.clone()

            for _ in range(abs(round(current_expand))):
                if current_expand < 0:
                    output = morphology.erosion(output, kernel)
                else:
                    output = morphology.dilation(output, kernel)
            if current_expand < 0:
                current_expand -= abs(incremental_expandrate)
            else:
                current_expand += abs(incremental_expandrate)

            output = output.squeeze(0).squeeze(0)

            if alpha < 1.0 and previous_output is not None:
                output = alpha * output + (1 - alpha) * previous_output
            if decay < 1.0 and previous_output is not None:
                output += decay * previous_output
                output = output / output.max()
            previous_output = output
            out.append(output)

        if blur_radius != 0:
            kernel_size = int(4 * round(blur_radius) + 1)
            blurred = [
                filters.gaussian_blur2d(
                    tensor.unsqueeze(0).unsqueeze(0),
                    (kernel_size, kernel_size),
                    (blur_radius, blur_radius),
                ).squeeze(0)
                for tensor in out
            ]
            blurred = torch.cat(blurred, dim=0)
            blurred_mask = TensorImage(blurred).get_BWHC()
            inverted = 1.0 - blurred_mask

            return (
                blurred_mask,
                inverted,
            )

        unblurred = torch.stack(out, dim=0)
        unblurred_mask = TensorImage(unblurred).get_BWHC()
        inverted = 1 - unblurred_mask

        return (
            unblurred_mask,
            inverted,
        )
