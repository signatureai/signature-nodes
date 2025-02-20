import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import MASK_CAT


class MaskBitwise:
    """Performs bitwise logical operations between two binary masks.

    Converts masks to 8-bit format and applies various bitwise operations, useful for combining
    or comparing mask regions.

    Args:
        mask_1 (torch.Tensor): First input mask in BWHC format
        mask_2 (torch.Tensor): Second input mask in BWHC format
        mode (str): Bitwise operation to apply. Options:
            - "and": Intersection of masks
            - "or": Union of masks
            - "xor": Exclusive OR of masks
            - "left_shift": Left bit shift using mask_2 as shift amount
            - "right_shift": Right bit shift using mask_2 as shift amount

    Returns:
        tuple[torch.Tensor]: A single-element tuple containing the resulting mask in BWHC format

    Raises:
        ValueError: If mode is not one of the supported operations

    Notes:
        - Masks are converted to 8-bit (0-255) before operations and back to float (0-1) after
        - Shift operations use the second mask values as the number of bits to shift
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask_1": ("MASK",),
                "mask_2": ("MASK",),
                "mode": (["and", "or", "xor", "left_shift", "right_shift"],),
            },
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "execute"
    CATEGORY = MASK_CAT

    def execute(self, mask_1: torch.Tensor, mask_2: torch.Tensor, mode: str = "and") -> tuple[torch.Tensor]:
        input_mask_1 = TensorImage.from_BWHC(mask_1)
        input_mask_2 = TensorImage.from_BWHC(mask_2)
        eight_bit_mask_1 = torch.tensor(input_mask_1 * 255, dtype=torch.uint8)
        eight_bit_mask_2 = torch.tensor(input_mask_2 * 255, dtype=torch.uint8)

        try:
            result = getattr(torch, f"bitwise_{mode}")(eight_bit_mask_1, eight_bit_mask_2)
        except AttributeError:
            raise ValueError(f"Invalid mode: {mode}")

        float_result = result.float() / 255
        output_mask = TensorImage(float_result).get_BWHC()
        return (output_mask,)
