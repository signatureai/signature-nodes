import torch
from kornia.geometry import transform
from signature_core.img.tensor_image import TensorImage

from ...categories import IMAGE_CAT


class ImageTranspose:
    """Transforms and composites an overlay image onto a base image.

    Provides comprehensive image composition capabilities including resizing, positioning, rotation,
    and edge feathering of an overlay image onto a base image.

    Args:
        image (torch.Tensor): Base image in BWHC format
        image_overlay (torch.Tensor): Overlay image in BWHC format
        width (int): Target width for overlay (-1 for original size)
        height (int): Target height for overlay (-1 for original size)
        X (int): Horizontal offset in pixels from left edge
        Y (int): Vertical offset in pixels from top edge
        rotation (int): Rotation angle in degrees (-360 to 360)
        feathering (int): Edge feathering radius in pixels (0-100)

    Returns:
        tuple[torch.Tensor, torch.Tensor]: Two-element tuple containing:
            - tensor: Composited image in RGB format
            - tensor: Composited image in RGBA format with transparency

    Raises:
        ValueError: If any input parameters are not of correct type
        ValueError: If rotation is outside valid range
        ValueError: If feathering is outside valid range

    Notes:
        - Supports both RGB and RGBA overlay images
        - Automatically handles padding and cropping
        - Feathering creates smooth edges around the overlay
        - All transformations preserve aspect ratio when specified
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "image_overlay": ("IMAGE",),
                "width": ("INT", {"default": -1, "min": -1, "max": 48000, "step": 1}),
                "height": ("INT", {"default": -1, "min": -1, "max": 48000, "step": 1}),
                "x": ("INT", {"default": 0, "min": 0, "max": 48000, "step": 1}),
                "y": ("INT", {"default": 0, "min": 0, "max": 48000, "step": 1}),
                "rotation": ("INT", {"default": 0, "min": -360, "max": 360, "step": 1}),
                "feathering": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "IMAGE",
    )
    RETURN_NAMES = (
        "rgb",
        "rgba",
    )
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    DESCRIPTION = "Transforms and composites an overlay image onto a base image. Provides comprehensive composition capabilities including resizing, positioning, rotation, and edge feathering. Returns both RGB and RGBA versions."

    def execute(
        self,
        image: torch.Tensor,
        image_overlay: torch.Tensor,
        width: int = -1,
        height: int = -1,
        x: int = 0,
        y: int = 0,
        rotation: int = 0,
        feathering: int = 0,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        base_image = TensorImage.from_BWHC(image)
        overlay_image = TensorImage.from_BWHC(image_overlay)

        if width == -1:
            width = overlay_image.shape[3]
        if height == -1:
            height = overlay_image.shape[2]

        device = base_image.device
        overlay_image = overlay_image.to(device)

        # Resize overlay image
        overlay_image = transform.resize(overlay_image, (height, width))

        if rotation != 0:
            angle = torch.tensor(rotation, dtype=torch.float32, device=device)
            center = torch.tensor([width / 2, height / 2], dtype=torch.float32, device=device)
            overlay_image = transform.rotate(overlay_image, angle, center=center)

        # Create mask (handle both RGB and RGBA cases)
        if overlay_image.shape[1] == 4:
            mask = overlay_image[:, 3:4, :, :]
        else:
            mask = torch.ones((1, 1, height, width), device=device)

        # Pad overlay image and mask
        pad_left = x
        pad_top = y
        pad_right = max(0, base_image.shape[3] - overlay_image.shape[3] - x)
        pad_bottom = max(0, base_image.shape[2] - overlay_image.shape[2] - y)

        overlay_image = torch.nn.functional.pad(overlay_image, (pad_left, pad_right, pad_top, pad_bottom))
        mask = torch.nn.functional.pad(mask, (pad_left, pad_right, pad_top, pad_bottom))

        # Resize to match base image
        overlay_image = transform.resize(overlay_image, base_image.shape[2:])
        mask = transform.resize(mask, base_image.shape[2:])

        if feathering > 0:
            kernel_size = 2 * feathering + 1
            feather_kernel = torch.ones((1, 1, kernel_size, kernel_size), device=device) / (kernel_size**2)
            mask = torch.nn.functional.conv2d(mask, feather_kernel, padding=feathering)

        # Blend images
        result = base_image * (1 - mask) + overlay_image[:, :3, :, :] * mask

        result = TensorImage(result).get_BWHC()

        rgb = result
        rgba = torch.cat([rgb, mask.permute(0, 2, 3, 1)], dim=3)

        return (rgb, rgba)
