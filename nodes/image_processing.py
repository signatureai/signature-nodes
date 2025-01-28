import comfy  # type: ignore
import folder_paths  # type: ignore
import torch
from comfy import model_management  # type: ignore
from signature_core.functional.color import rgba_to_rgb
from signature_core.functional.transform import (
    auto_crop,
    cutout,
    rescale,
    resize,
    rotate,
)
from signature_core.img.tensor_image import TensorImage
from spandrel import ImageModelDescriptor, ModelLoader  # type: ignore

from .categories import IMAGE_PROCESSING_CAT


class AutoCrop:
    """Automatically crops an image based on a mask content.

    This node detects non-zero regions in a mask and crops both the image and mask
    to those regions, with optional padding. Useful for removing empty space around
    subjects or focusing on specific masked areas.

    Args:
        image (torch.Tensor): Input image tensor in BWHC format with values in range [0, 1]
        mask (torch.Tensor): Input mask tensor in BWHC format with values in range [0, 1]
        mask_threshold (float): Minimum mask value to consider as content (0.0-1.0)
        left_padding (int): Additional pixels to include on the left side
        right_padding (int): Additional pixels to include on the right side
        top_padding (int): Additional pixels to include on the top
        bottom_padding (int): Additional pixels to include on the bottom

    Returns:
        tuple:
            - cropped_image (torch.Tensor): Cropped image in BWHC format
            - cropped_mask (torch.Tensor): Cropped mask in BWHC format
            - x (int): X-coordinate of crop start in original image
            - y (int): Y-coordinate of crop start in original image
            - width (int): Width of cropped region
            - height (int): Height of cropped region

    Raises:
        ValueError: If mask and image dimensions don't match
        RuntimeError: If no content is found in mask above threshold

    Notes:
        - Input tensors should be in BWHC format (Batch, Width, Height, Channels)
        - Mask should be single-channel
        - All padding values must be non-negative
        - If mask is empty above threshold, may return minimal crop
        - Coordinates are returned relative to original image
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "mask_threshold": ("FLOAT", {"default": 0.1, "min": 0.00, "max": 1.00, "step": 0.01}),
                "left_padding": ("INT", {"default": 0}),
                "right_padding": ("INT", {"default": 0}),
                "top_padding": ("INT", {"default": 0}),
                "bottom_padding": ("INT", {"default": 0}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("cropped_image", "cropped_mask", "x", "y", "width", "height")

    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT

    def execute(self, **kwargs):
        img_tensor = TensorImage.from_BWHC(kwargs["image"])
        mask_tensor = TensorImage.from_BWHC(kwargs["mask"])
        if img_tensor.shape[1] != 3:
            img_tensor = rgba_to_rgb(img_tensor)

        padding = (
            kwargs["left_padding"],
            kwargs["right_padding"],
            kwargs["top_padding"],
            kwargs["bottom_padding"],
        )
        img_result, mask_result, min_x, min_y, width, height = auto_crop(
            img_tensor, mask_tensor, mask_threshold=kwargs["mask_threshold"], padding=padding
        )
        output_img = TensorImage(img_result).get_BWHC()
        output_mask = TensorImage(mask_result).get_BWHC()

        return (output_img, output_mask, min_x, min_y, width, height)


class Rescale:
    """Rescales images and masks by a specified factor while preserving aspect ratio.

    Provides flexible rescaling of images and masks with support for various interpolation
    methods and optional antialiasing. Useful for uniform scaling operations where
    maintaining aspect ratio is important.

    Args:
        image (torch.Tensor, optional): Input image in BWHC format with values in range [0, 1]
        mask (torch.Tensor, optional): Input mask in BWHC format with values in range [0, 1]
        factor (float): Scale multiplier (0.01-100.0)
        interpolation (str): Resampling method to use:
            - "nearest": Nearest neighbor (sharp, blocky)
            - "nearest-exact": Nearest neighbor without rounding
            - "bilinear": Linear interpolation (smooth)
            - "bicubic": Cubic interpolation (smoother)
            - "box": Box sampling (good for downscaling)
            - "hamming": Hamming windowed sampling
            - "lanczos": Lanczos resampling (sharp, fewer artifacts)
        antialias (bool): Whether to apply antialiasing when downscaling

    Returns:
        tuple:
            - image (torch.Tensor): Rescaled image in BWHC format
            - mask (torch.Tensor): Rescaled mask in BWHC format

    Raises:
        ValueError: If neither image nor mask is provided
        ValueError: If invalid interpolation method specified
        RuntimeError: If input tensors have invalid dimensions

    Notes:
        - At least one of image or mask must be provided
        - Output maintains the same number of channels as input
        - Antialiasing is recommended when downscaling to prevent artifacts
        - All interpolation methods preserve the value range [0, 1]
        - Memory usage scales quadratically with factor
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {},
            "optional": {
                "image": ("IMAGE", {"default": None}),
                "mask": ("MASK", {"default": None}),
                "factor": ("FLOAT", {"default": 2.0, "min": 0.01, "max": 100.0, "step": 0.01}),
                "interpolation": (["nearest", "nearest-exact", "bilinear", "bicubic", "box", "hamming", "lanczos"],),
                "antialias": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT

    def execute(self, **kwargs):
        image = kwargs.get("image")
        mask = kwargs.get("mask")
        if not isinstance(image, torch.Tensor) and not isinstance(mask, torch.Tensor):
            raise ValueError("Either image or mask must be provided")

        input_image = (
            TensorImage.from_BWHC(image) if isinstance(image, torch.Tensor) else TensorImage(torch.zeros((1, 3, 1, 1)))
        )
        input_mask = (
            TensorImage.from_BWHC(mask) if isinstance(mask, torch.Tensor) else TensorImage(torch.zeros((1, 1, 1, 1)))
        )
        output_image = rescale(
            input_image,
            kwargs.get("factor", 2.0),
            kwargs.get("interpolation", "nearest"),
            kwargs.get("antialias", True),
        ).get_BWHC()
        output_mask = rescale(
            input_mask,
            kwargs.get("factor", 2.0),
            kwargs.get("interpolation", "nearest"),
            kwargs.get("antialias", True),
        ).get_BWHC()

        return (
            output_image,
            output_mask,
        )


class Resize:
    """Resizes images and masks to specific dimensions with multiple sizing modes.

    A versatile resizing node that supports multiple modes for handling aspect ratio
    and provides fine control over interpolation methods. Suitable for preparing
    images for specific size requirements while maintaining quality.

    Args:
        image (torch.Tensor, optional): Input image in BWHC format with values in range [0, 1]
        mask (torch.Tensor, optional): Input mask in BWHC format with values in range [0, 1]
        width (int): Target width in pixels (32-40960)
        height (int): Target height in pixels (32-40960)
        mode (str): How to handle aspect ratio:
            - "STRETCH": Force to exact dimensions, may distort
            - "FIT": Fit within dimensions, may be smaller
            - "FILL": Fill dimensions, may crop
            - "ASPECT": Preserve aspect ratio, fit longest side
        interpolation (str): Resampling method:
            - "bilinear": Linear interpolation (smooth)
            - "nearest": Nearest neighbor (sharp)
            - "bicubic": Cubic interpolation (smoother)
            - "area": Area averaging (good for downscaling)
        antialias (bool): Whether to apply antialiasing when downscaling

    Returns:
        tuple:
            - image (torch.Tensor): Resized image in BWHC format
            - mask (torch.Tensor): Resized mask in BWHC format

    Raises:
        ValueError: If neither image nor mask is provided
        ValueError: If dimensions are out of valid range
        ValueError: If invalid mode or interpolation method
        RuntimeError: If input tensors have invalid dimensions

    Notes:
        - At least one of image or mask must be provided
        - Output maintains the same number of channels as input
        - STRETCH mode may distort image proportions
        - FIT mode ensures no cropping but may not fill target size
        - FILL mode ensures target size but may crop content
        - ASPECT mode preserves proportions using longest edge
        - Antialiasing recommended when downscaling
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {},
            "optional": {
                "image": ("IMAGE", {"default": None}),
                "mask": ("MASK", {"default": None}),
                "width": ("INT", {"default": 1024, "min": 32, "step": 2, "max": 40960}),
                "height": ("INT", {"default": 1024, "min": 32, "step": 2, "max": 40960}),
                "mode": (["STRETCH", "FIT", "FILL", "ASPECT"],),
                "interpolation": (["bilinear", "nearest", "bicubic", "area"],),
                "antialias": (
                    "BOOLEAN",
                    {"default": True},
                ),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT

    def execute(self, **kwargs):
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 1024)
        mode = kwargs.get("mode", "default")
        interpolation = kwargs.get("interpolation", "nearest")
        antialias = kwargs.get("antialias", True)
        image = kwargs.get("image", None)
        mask = kwargs.get("mask", None)

        input_image = (
            TensorImage.from_BWHC(image)
            if isinstance(image, torch.Tensor)
            else TensorImage(torch.zeros((1, 3, width, height)))
        )
        input_mask = (
            TensorImage.from_BWHC(mask)
            if isinstance(mask, torch.Tensor)
            else TensorImage(torch.zeros((1, 1, width, height)))
        )
        output_image = resize(input_image, width, height, mode, interpolation, antialias).get_BWHC()
        output_mask = resize(input_mask, width, height, mode, interpolation, antialias).get_BWHC()

        return (
            output_image,
            output_mask,
        )


class Rotate:
    """Rotates images and masks by a specified angle with optional zoom adjustment.

    Performs rotation of images and masks with control over whether to zoom to fit
    the entire rotated content. Useful for reorienting content while managing the
    trade-off between content preservation and output size.

    Args:
        image (torch.Tensor, optional): Input image in BWHC format with values in range [0, 1]
        mask (torch.Tensor, optional): Input mask in BWHC format with values in range [0, 1]
        angle (float): Rotation angle in degrees (0-360)
        zoom_to_fit (bool): Whether to zoom out to show all rotated content

    Returns:
        tuple:
            - image (torch.Tensor): Rotated image in BWHC format
            - mask (torch.Tensor): Rotated mask in BWHC format

    Raises:
        ValueError: If neither image nor mask is provided
        ValueError: If angle is outside valid range
        RuntimeError: If input tensors have invalid dimensions

    Notes:
        - At least one of image or mask must be provided
        - Rotation is performed counterclockwise
        - When zoom_to_fit is False, corners may be clipped
        - When zoom_to_fit is True, output may be larger
        - Interpolation is bilinear for smooth results
        - Empty areas after rotation are filled with black
        - Maintains aspect ratio of input
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "image": ("IMAGE", {"default": None}),
                "mask": ("MASK", {"default": None}),
                "angle": ("FLOAT", {"default": 0.0, "min": 0, "max": 360.0, "step": 1.0}),
                "zoom_to_fit": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT

    def execute(self, **kwargs):
        image = kwargs.get("image", None)
        mask = kwargs.get("mask", None)
        angle = kwargs.get("angle", 0.0)
        zoom_to_fit = kwargs.get("zoom_to_fit", False)

        input_image = (
            TensorImage.from_BWHC(image) if isinstance(image, torch.Tensor) else TensorImage(torch.zeros((1, 3, 1, 1)))
        )
        input_mask = (
            TensorImage.from_BWHC(mask) if isinstance(mask, torch.Tensor) else TensorImage(torch.zeros((1, 1, 1, 1)))
        )
        output_image = rotate(input_image, angle, zoom_to_fit).get_BWHC()
        output_mask = rotate(input_mask, angle, zoom_to_fit).get_BWHC()

        return (
            output_image,
            output_mask,
        )


class Cutout:
    """Creates masked cutouts from images with both RGB and RGBA outputs.

    Extracts portions of an image based on a mask, providing both RGB and RGBA
    versions of the result. Useful for isolating subjects or creating transparent
    cutouts for compositing.

    Args:
        image (torch.Tensor): Input image in BWHC format with values in range [0, 1]
        mask (torch.Tensor): Binary or continuous mask in BWHC format with values in range [0, 1]

    Returns:
        tuple:
            - rgb (torch.Tensor): Masked image in RGB format (BWHC)
            - rgba (torch.Tensor): Masked image in RGBA format (BWHC)

    Raises:
        ValueError: If either image or mask is not provided
        ValueError: If input tensors have mismatched dimensions
        RuntimeError: If input tensors have invalid dimensions

    Notes:
        - Mask values determine transparency in RGBA output
        - RGB output has masked areas filled with black
        - RGBA output preserves partial mask values as alpha
        - Input image must be 3 channels (RGB)
        - Input mask must be 1 channel
        - Output maintains original image resolution
        - All non-zero mask values are considered for cutout
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
            },
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("rgb", "rgba")
    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT

    def execute(self, **kwargs):
        image = kwargs.get("image")
        mask = kwargs.get("mask")

        if not isinstance(image, torch.Tensor) or not isinstance(mask, torch.Tensor):
            raise ValueError("Either image or mask must be provided")

        tensor_image = TensorImage.from_BWHC(image)
        tensor_mask = TensorImage.from_BWHC(mask, image.device)

        image_rgb, image_rgba = cutout(tensor_image, tensor_mask)

        out_image_rgb = TensorImage(image_rgb).get_BWHC()
        out_image_rgba = TensorImage(image_rgba).get_BWHC()

        return (
            out_image_rgb,
            out_image_rgba,
        )


class UpscaleImage:
    """AI-powered image upscaling with tiled processing and flexible scaling modes.

    A comprehensive image upscaling node that leverages AI models for high-quality image enlargement.
    Supports both factor-based rescaling and target size resizing while efficiently managing GPU
    memory through tiled processing. Compatible with various AI upscaling models and includes
    multiple resampling methods for final adjustments.

    Args:
        image (torch.Tensor): Input image tensor in BCHW format with values in range [0, 1].
        upscale_model (str): Filename of the AI upscaling model to use.
        mode (str): Scaling mode, either:
            - "rescale": Scale relative to original size by a factor
            - "resize": Scale to a specific target size
        rescale_factor (float, optional): Scaling multiplier when using "rescale" mode.
            Defaults to 2.0.
        resize_size (int, optional): Target size in pixels for longest edge when using "resize" mode.
            Defaults to 1024.
        resampling_method (str, optional): Final resampling method for precise size adjustment.
            Options: "bilinear", "nearest", "bicubic", "area". Defaults to "bilinear".
        tiled_size (int, optional): Size of processing tiles in pixels. Larger tiles use more GPU memory.
            Defaults to 512.

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - image (torch.Tensor): Upscaled image in BCHW format with values in range [0, 1]

    Raises:
        ValueError: If the upscale model is invalid or incompatible
        RuntimeError: If GPU memory is insufficient even with minimum tile size
        TypeError: If input tensors are of incorrect type

    Notes:
        - Models are loaded from the "upscale_models" directory
        - Processing is done in tiles to manage GPU memory efficiently
        - For large upscaling factors, multiple passes may be performed
        - The aspect ratio is always preserved in "resize" mode
        - If GPU memory is insufficient, tile size is automatically reduced
        - Tiled processing may show slight seams with some models
        - Final output is always clamped to [0, 1] range
        - Model scale factor is automatically detected and respected
        - Progress bar shows processing status for large images
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        resampling_methods = ["bilinear", "nearest", "bicubic", "area"]

        return {
            "required": {
                "image": ("IMAGE",),
                "upscale_model": (folder_paths.get_filename_list("upscale_models"),),
                "mode": (["rescale", "resize"],),
                "rescale_factor": ("FLOAT", {"default": 2, "min": 0.01, "max": 100.0, "step": 0.01}),
                "resize_size": ("INT", {"default": 1024, "min": 1, "max": 48000, "step": 1}),
                "resampling_method": (resampling_methods,),
                "tiled_size": ("INT", {"default": 512, "min": 128, "max": 2048, "step": 128}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT

    def load_model(self, model_name):
        model_path = folder_paths.get_full_path("upscale_models", model_name)
        sd = comfy.utils.load_torch_file(model_path, safe_load=True)
        if "module.layers.0.residual_group.blocks.0.norm1.weight" in sd:
            sd = comfy.utils.state_dict_prefix_replace(sd, {"module.": ""})
        out = ModelLoader().load_from_state_dict(sd)

        if not isinstance(out, ImageModelDescriptor):
            raise ValueError("Upscale model must be a single-image model.")

        return out

    def upscale_with_model(self, **kwargs) -> torch.Tensor:
        upscale_model = kwargs.get("upscale_model")
        image = kwargs.get("image")
        device = kwargs.get("device")
        tile = kwargs.get("tile", 512)
        overlap = kwargs.get("overlap", 32)

        if upscale_model is None:
            raise ValueError("upscale_model is required")
        if image is None:
            raise ValueError("image is required")
        if device is None:
            raise ValueError("device is required")
        if not isinstance(tile, int):
            raise ValueError("tile must be an integer")
        if not isinstance(overlap, int):
            raise ValueError("overlap must be an integer")
        if not hasattr(upscale_model, "model"):
            raise ValueError("upscale_model must have a model attribute")
        if not hasattr(upscale_model, "scale"):
            raise ValueError("upscale_model must have a scale attribute")
        if not isinstance(image, torch.Tensor):
            raise ValueError("image must be a torch.Tensor")

        memory_required = model_management.module_size(upscale_model.model)
        memory_required += (tile * tile * 3) * image.element_size() * max(upscale_model.scale, 1.0) * 384.0
        memory_required += image.nelement() * image.element_size()
        model_management.free_memory(memory_required, device)
        in_img = image.movedim(-1, -3).to(device)

        s = None
        oom = True
        while oom:
            try:
                steps = in_img.shape[0] * comfy.utils.get_tiled_scale_steps(
                    in_img.shape[3], in_img.shape[2], tile_x=tile, tile_y=tile, overlap=overlap
                )
                pbar = comfy.utils.ProgressBar(steps)
                s = comfy.utils.tiled_scale(
                    in_img,
                    lambda a: upscale_model(a),
                    tile_x=tile,
                    tile_y=tile,
                    overlap=overlap,
                    upscale_amount=upscale_model.scale,
                    pbar=pbar,
                )
                oom = False
            except model_management.OOM_EXCEPTION as e:
                tile //= 2
                if tile < 128:
                    raise e

        if not isinstance(s, torch.Tensor):
            raise ValueError("Upscaling failed")
        s = torch.clamp(s.movedim(-3, -1), min=0, max=1.0)  # type: ignore
        return s

    def execute(self, image, upscale_model, **kwargs):
        # Load upscale model
        up_model = self.load_model(upscale_model)
        device = model_management.get_torch_device()
        up_model.to(device)

        # Get kwargs with defaults
        mode = kwargs.get("mode", "rescale")
        resampling_method = kwargs.get("resampling_method", "bilinear")
        rescale_factor = kwargs.get("rescale_factor", 2)
        resize_size = kwargs.get("resize_size", 1024)
        tiled_size = kwargs.get("tiled_size", 512)

        # target size
        _, H, W, _ = image.shape
        target_size = resize_size if mode == "resize" else max(H, W) * rescale_factor
        current_size = max(H, W)
        up_image = image
        while current_size < target_size:
            step = self.upscale_with_model(upscale_model=up_model, image=up_image, device=device, tile=tiled_size)
            del up_image
            up_image = step.to("cpu")
            _, H, W, _ = up_image.shape
            current_size = max(H, W)

        up_model.to("cpu")
        tensor_image = TensorImage.from_BWHC(up_image)

        if mode == "resize":
            up_image = resize(tensor_image, resize_size, resize_size, "ASPECT", resampling_method, True).get_BWHC()
        else:
            # get the max size of the upscaled image
            _, _, H, W = tensor_image.shape
            upscaled_max_size = max(H, W)

            original_image = TensorImage.from_BWHC(image)
            _, _, ori_H, ori_W = original_image.shape
            original_max_size = max(ori_H, ori_W)

            # rescale_factor is the factor to multiply the original max size
            original_target_size = rescale_factor * original_max_size
            scale_factor = original_target_size / upscaled_max_size

            up_image = rescale(tensor_image, scale_factor, resampling_method, True).get_BWHC()

        return (up_image,)
