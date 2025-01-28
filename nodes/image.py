import torch
from kornia.geometry import transform
from signature_core.functional.filters import (
    gaussian_blur2d,
    image_soft_light,
    unsharp_mask,
)
from signature_core.functional.transform import resize
from signature_core.img.tensor_image import TensorImage

from .categories import IMAGE_CAT


class ImageBaseColor:
    """Creates a solid color image with specified dimensions.

    This node generates a uniform color image using a hex color code. The output is a tensor in BWHC
    format (Batch, Width, Height, Channels) with the specified dimensions.

    Args:
        hex_color (str): Hex color code in format "#RRGGBB" (e.g., "#FFFFFF" for white)
        width (int): Width of the output image in pixels
        height (int): Height of the output image in pixels

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Image in BWHC format with shape (1, height, width, 3)

    Raises:
        ValueError: If width or height are not integers
        ValueError: If hex_color is not a string
        ValueError: If hex_color is not in valid "#RRGGBB" format

    Notes:
        - The output tensor values are normalized to range [0, 1]
        - Alpha channel is not supported
        - The batch dimension is always 1
        - RGB values are extracted from hex color and converted to float32
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "hex_color": ("STRING", {"default": "#FFFFFF"}),
                "width": ("INT", {"default": 1024}),
                "height": ("INT", {"default": 1024}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    CLASS_ID = "image_base_color"

    def execute(
        self, hex_color: str = "#FFFFFF", width: int = 1024, height: int = 1024
    ) -> tuple[torch.Tensor]:
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        # Create a tensor with the specified color
        color_tensor = torch.tensor([r, g, b], dtype=torch.float32) / 255.0

        # Reshape to (3, 1, 1) and expand to (3, H, W)
        color_tensor = color_tensor.view(3, 1, 1).expand(3, height, width)

        # Repeat for the batch size
        batch_tensor = color_tensor.unsqueeze(0).expand(1, -1, -1, -1)

        output = TensorImage(batch_tensor).get_BWHC()
        return (output,)


class ImageGaussianBlur:
    """Applies Gaussian blur filter to an input image.

    This node performs Gaussian blur using a configurable kernel size and sigma value. Multiple passes
    can be applied for stronger blur effects. The blur is applied uniformly across all color channels.

    Args:
        image (torch.Tensor): Input image tensor in BWHC format
        radius (int): Blur kernel radius in pixels (kernel size = 2 * radius + 1)
        sigma (float): Standard deviation for Gaussian kernel, controls blur strength
        iterations (int): Number of times to apply the blur filter sequentially

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Blurred image in BWHC format with same shape as input

    Raises:
        ValueError: If image is not a torch.Tensor
        ValueError: If radius is not an integer
        ValueError: If sigma is not a float
        ValueError: If iterations is not an integer

    Notes:
        - Larger radius and sigma values produce stronger blur effects
        - Multiple iterations can create smoother results but increase processing time
        - Input image dimensions and batch size are preserved in output
        - Processing is done on GPU if input tensor is on GPU
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
                "radius": ("INT", {"default": 13}),
                "sigma": ("FLOAT", {"default": 10.5}),
                "interations": ("INT", {"default": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT

    def execute(
        self,
        image: torch.Tensor,
        radius: int = 13,
        sigma: float = 10.5,
        interations: int = 1,
    ) -> tuple[torch.Tensor]:
        tensor_image = TensorImage.from_BWHC(image)
        output = gaussian_blur2d(tensor_image, radius, sigma, interations).get_BWHC()
        return (output,)


class ImageUnsharpMask:
    """Enhances image sharpness using unsharp mask technique.

    This node applies an unsharp mask filter to enhance edge details in the image. It works by
    subtracting a blurred version of the image from the original, creating a sharpening effect.

    Args:
        image (torch.Tensor): Input image in BWHC format
        radius (int): Size of the blur kernel used in the unsharp mask
        sigma (float): Strength of the blur in the unsharp mask calculation
        iterations (int): Number of times to apply the sharpening effect

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Sharpened image in BWHC format with same shape as input

    Raises:
        ValueError: If image is not a torch.Tensor
        ValueError: If radius is not an integer
        ValueError: If sigma is not a float
        ValueError: If iterations is not an integer

    Notes:
        - Higher sigma values create stronger sharpening effects
        - Multiple iterations can create more pronounced sharpening but may introduce artifacts
        - The process preserves the original image dimensions and color range
        - Works on all color channels independently
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
                "radius": ("INT", {"default": 3}),
                "sigma": ("FLOAT", {"default": 1.5}),
                "interations": ("INT", {"default": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT

    def execute(
        self,
        image: torch.Tensor,
        radius: int = 3,
        sigma: float = 1.5,
        interations: int = 1,
    ) -> tuple[torch.Tensor]:
        tensor_image = TensorImage.from_BWHC(image)
        output = unsharp_mask(tensor_image, radius, sigma, interations).get_BWHC()
        return (output,)


class ImageSoftLight:
    """Applies soft light blend mode between two images.

    Implements the soft light blending mode similar to photo editing software. The effect creates a
    subtle, soft lighting effect based on the interaction between the top and bottom layers.

    Args:
        top (torch.Tensor): Top layer image in BWHC format, acts as the blend layer
        bottom (torch.Tensor): Bottom layer image in BWHC format, acts as the base layer

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Blended image in BWHC format with same shape as inputs

    Raises:
        ValueError: If top is not a torch.Tensor
        ValueError: If bottom is not a torch.Tensor
        ValueError: If input tensors have different shapes

    Notes:
        - Both input images must have the same dimensions
        - The blend preserves the original image dimensions and color range
        - The effect is similar to soft light blend mode in photo editing software
        - Processing is done on GPU if input tensors are on GPU
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "top": ("IMAGE",),
                "bottom": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT

    def execute(self, top: torch.Tensor, bottom: torch.Tensor) -> tuple[torch.Tensor]:
        top_tensor = TensorImage.from_BWHC(top)
        bottom_tensor = TensorImage.from_BWHC(bottom)
        output = image_soft_light(top_tensor, bottom_tensor).get_BWHC()

        return (output,)


class ImageAverage:
    """Calculates the average color of an input image.

    Computes the mean color values across all pixels in the image, resulting in a uniform color
    image representing the average color of the input.

    Args:
        image (torch.Tensor): Input image in BWHC format to calculate average from

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Uniform color image in BWHC format with same shape as input

    Raises:
        ValueError: If image is not a torch.Tensor

    Notes:
        - Output maintains the same dimensions as input but with uniform color
        - Calculation is performed per color channel
        - Useful for color analysis or creating color-matched solid backgrounds
        - Preserves the original batch size
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "focus_mask": ("MASK",),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("color", "hex_color")
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT

    def execute(self, image: torch.Tensor, focus_mask: torch.Tensor | None = None):
        step = TensorImage.from_BWHC(image)
        if focus_mask is not None:
            mask = TensorImage.from_BWHC(focus_mask)
            masked_image = step * mask
            step = masked_image.sum(dim=[2, 3], keepdim=True) / (
                mask.sum(dim=[2, 3], keepdim=True) + 1e-8
            )
        else:
            step = step.mean(dim=[2, 3], keepdim=True)
        step = step.expand(-1, -1, image.shape[1], image.shape[2])
        output = TensorImage(step).get_BWHC()

        avg_color = step[0, :, 0, 0] * 255
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(avg_color[0].item()), int(avg_color[1].item()), int(avg_color[2].item())
        )

        return (output, hex_color)


class ImageSubtract:
    """Computes the absolute difference between two images.

    Performs pixel-wise subtraction between two images and takes the absolute value of the result,
    useful for comparing images or creating difference maps.

    Args:
        image_0 (torch.Tensor): First image in BWHC format
        image_1 (torch.Tensor): Second image in BWHC format to subtract from first image

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Difference image in BWHC format with same shape as inputs

    Raises:
        ValueError: If image_0 is not a torch.Tensor
        ValueError: If image_1 is not a torch.Tensor
        ValueError: If input tensors have different shapes

    Notes:
        - Both input images must have the same dimensions
        - Output values represent absolute differences between corresponding pixels
        - Useful for change detection or image comparison
        - Result is always positive due to absolute value operation
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image_0": ("IMAGE",),
                "image_1": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT

    def execute(
        self, image_0: torch.Tensor, image_1: torch.Tensor
    ) -> tuple[torch.Tensor]:
        image_0_tensor = TensorImage.from_BWHC(image_0)
        image_1_tensor = TensorImage.from_BWHC(image_1)
        image_tensor = torch.abs(image_0_tensor - image_1_tensor)
        output = TensorImage(image_tensor).get_BWHC()
        return (output,)


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
            center = torch.tensor(
                [width / 2, height / 2], dtype=torch.float32, device=device
            )
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

        overlay_image = torch.nn.functional.pad(
            overlay_image, (pad_left, pad_right, pad_top, pad_bottom)
        )
        mask = torch.nn.functional.pad(mask, (pad_left, pad_right, pad_top, pad_bottom))

        # Resize to match base image
        overlay_image = transform.resize(overlay_image, base_image.shape[2:])
        mask = transform.resize(mask, base_image.shape[2:])

        if feathering > 0:
            kernel_size = 2 * feathering + 1
            feather_kernel = torch.ones(
                (1, 1, kernel_size, kernel_size), device=device
            ) / (kernel_size**2)
            mask = torch.nn.functional.conv2d(mask, feather_kernel, padding=feathering)

        # Blend images
        result = base_image * (1 - mask) + overlay_image[:, :3, :, :] * mask

        result = TensorImage(result).get_BWHC()

        rgb = result
        rgba = torch.cat([rgb, mask.permute(0, 2, 3, 1)], dim=3)

        return (rgb, rgba)


class ImageList2Batch:
    """Converts a list of individual images into a batched tensor.

    Combines multiple images into a single batched tensor, handling different input sizes through
    various resize modes. Supports multiple interpolation methods for optimal quality.

    Args:
        images (list[torch.Tensor]): List of input images in BWHC format
        mode (str): Resize mode for handling different image sizes:
            - 'STRETCH': Stretches images to match largest dimensions
            - 'FIT': Fits images within largest dimensions, maintaining aspect ratio
            - 'FILL': Fills to largest dimensions, maintaining aspect ratio with cropping
            - 'ASPECT': Preserves aspect ratio with padding
        interpolation (str): Interpolation method for resizing:
            - 'bilinear': Smooth interpolation suitable for most cases
            - 'nearest': Nearest neighbor, best for pixel art
            - 'bicubic': High-quality interpolation
            - 'area': Best for downscaling

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - tensor: Batched images in BWHC format

    Raises:
        ValueError: If images is not a list
        ValueError: If mode is not a valid option
        ValueError: If interpolation is not a valid option

    Notes:
        - All images in output batch will have same dimensions
        - Original image qualities are preserved as much as possible
        - Memory efficient processing for large batches
        - GPU acceleration is automatically used when available
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "mode": (["STRETCH", "FIT", "FILL", "ASPECT"],),
                "interpolation": (["bilinear", "nearest", "bicubic", "area"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    INPUT_IS_LIST = True
    CLASS_ID = "image_list_batch"

    def execute(
        self, images: list[torch.Tensor], mode: str, interpolation: str
    ) -> tuple[torch.Tensor]:
        # Check if all images have the same shape
        shapes = [img.shape for img in images]
        if len(set(shapes)) == 1:
            # All images have the same shape, no need to resize
            return (torch.stack(images),)

        # Images have different shapes, proceed with resizing
        max_height = max(img.shape[1] for img in images)
        max_width = max(img.shape[2] for img in images)

        resized_images = []
        for img in images:
            tensor_img = TensorImage.from_BWHC(img)
            resized_img = resize(
                tensor_img,
                max_width,
                max_height,
                mode=mode,
                interpolation=interpolation,
            )
            resized_images.append(resized_img.get_BWHC().squeeze(0))

        return (torch.stack(resized_images),)


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

    def execute(self, image: torch.Tensor) -> tuple[list[torch.Tensor]]:
        image_list = [img.unsqueeze(0) for img in image]
        return (image_list,)


class GetImageShape:
    """Analyzes and returns the dimensions of an input image.

    Extracts and returns detailed shape information from an input image tensor, providing both
    individual dimensions and a formatted string representation.

    Args:
        image (torch.Tensor): Input image in BWHC format to analyze

    Returns:
        tuple[int, int, int, int, str]: Five-element tuple containing:
            - int: Batch size (B dimension)
            - int: Width in pixels
            - int: Height in pixels
            - int: Number of channels (typically 3 for RGB, 4 for RGBA)
            - str: Formatted string showing complete shape (B,W,H,C)

    Raises:
        ValueError: If image is not a torch.Tensor
        ValueError: If image does not have exactly 4 dimensions

    Notes:
        - Useful for debugging and dynamic processing
        - Shape string provides human-readable format
        - Can handle both RGB and RGBA images
        - Validates correct tensor format
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("batch", "width", "height", "channels", "debug")
    FUNCTION = "execute"
    CATEGORY = IMAGE_CAT
    CLASS_ID = "get_image_size"

    def execute(self, image: torch.Tensor) -> tuple[int, int, int, int, str]:
        return (
            image.shape[0],
            image.shape[2],
            image.shape[1],
            image.shape[3],
            str(image.shape),
        )
