import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import FILE_CAT


class Base64FromImage:
    """Converts ComfyUI image tensors to base64-encoded strings.

    Transforms image tensors from ComfyUI's format into base64-encoded strings, suitable for web
    transmission or storage in text format.

    Args:
        image (torch.Tensor): BWHC format tensor with values in [0,1] range.

    Returns:
        tuple[str]:
            - base64_str: PNG-encoded image as base64 string without data URL prefix

    Raises:
        ValueError: If input is not a tensor or has invalid format
        RuntimeError: If tensor conversion or encoding fails

    Notes:
        - Output is always PNG encoded
        - Preserves alpha channel if present
        - No data URL prefix in output
        - Maintains original image quality
        - Suitable for web APIs and storage
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {"required": {"image": ("IMAGE",)}}

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = FILE_CAT
    OUTPUT_NODE = True
    DESCRIPTION = """
    Converts images to base64-encoded strings (PNG format).
    Creates text representations of images suitable for web transmission, APIs,
    or text-based storage without data URL prefix."""

    def execute(self, image: torch.Tensor) -> tuple[str]:
        images = TensorImage.from_BWHC(image)
        output = images.get_base64()
        return (output,)
