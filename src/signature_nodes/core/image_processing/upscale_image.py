from typing import Optional

import comfy  # type: ignore
import folder_paths  # type: ignore
import torch
from signature_core.functional.transform import (
    rescale,
    resize,
)
from signature_core.img.tensor_image import TensorImage
from spandrel import ImageModelDescriptor, ModelLoader

from ...categories import IMAGE_PROCESSING_CAT


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
                "rescale_factor": (
                    "FLOAT",
                    {"default": 2, "min": 0.01, "max": 100.0, "step": 0.01},
                ),
                "resize_size": (
                    "INT",
                    {"default": 1024, "min": 1, "max": 48000, "step": 1},
                ),
                "resampling_method": (resampling_methods,),
                "tiled_size": (
                    "INT",
                    {"default": 512, "min": 128, "max": 2048, "step": 128},
                ),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = IMAGE_PROCESSING_CAT
    DESCRIPTION = """
    AI-powered image upscaling with tiled processing and flexible scaling modes.
    Leverages AI models for high-quality enlargement with options for factor-based rescaling or target size resizing.
    Efficiently manages GPU memory through tiled processing.
    """

    def load_model(self, model_name):
        model_path = folder_paths.get_full_path("upscale_models", model_name)
        sd = comfy.utils.load_torch_file(model_path, safe_load=True)
        if "module.layers.0.residual_group.blocks.0.norm1.weight" in sd:
            sd = comfy.utils.state_dict_prefix_replace(sd, {"module.": ""})
        out = ModelLoader().load_from_state_dict(sd)

        if not isinstance(out, ImageModelDescriptor):
            raise ValueError("Upscale model must be a single-image model.")

        return out

    def upscale_with_model(
        self,
        image: torch.Tensor,
        upscale_model: Optional[ImageModelDescriptor],
        device: Optional[torch.device],
        tile: int = 512,
        overlap: int = 32,
    ) -> torch.Tensor:
        if upscale_model is None:
            raise ValueError("upscale_model is required")
        if device is None:
            raise ValueError("device is required")
        if not hasattr(upscale_model, "model"):
            raise ValueError("upscale_model must have a model attribute")
        if not hasattr(upscale_model, "scale"):
            raise ValueError("upscale_model must have a scale attribute")

        memory_required = comfy.model_management.module_size(upscale_model.model)
        memory_required += (tile * tile * 3) * image.element_size() * max(upscale_model.scale, 1.0) * 384.0
        memory_required += image.nelement() * image.element_size()
        comfy.model_management.free_memory(memory_required, device)
        in_img = image.movedim(-1, -3).to(device)

        s = None
        oom = True
        while oom:
            try:
                steps = in_img.shape[0] * comfy.utils.get_tiled_scale_steps(
                    in_img.shape[3],
                    in_img.shape[2],
                    tile_x=tile,
                    tile_y=tile,
                    overlap=overlap,
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
            except comfy.model_management.OOM_EXCEPTION as e:
                tile //= 2
                if tile < 128:
                    raise e

        if not isinstance(s, torch.Tensor):
            raise ValueError("Upscaling failed")
        s = torch.clamp(s.movedim(-3, -1), min=0, max=1.0)  # type: ignore
        return s

    def execute(
        self,
        image: torch.Tensor,
        upscale_model: str,
        mode: str = "rescale",
        rescale_factor: float = 2,
        resize_size: int = 1024,
        resampling_method: str = "bilinear",
        tiled_size: int = 512,
    ):
        # Load upscale model
        up_model = self.load_model(upscale_model)
        device = comfy.model_management.get_torch_device()
        up_model.to(device)

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
            up_image = resize(
                tensor_image,
                resize_size,
                resize_size,
                "ASPECT",
                resampling_method,
                True,
            ).get_BWHC()
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
