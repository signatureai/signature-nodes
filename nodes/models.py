import random

import comfy.model_management  # type: ignore
import folder_paths  # type: ignore
import torch
from comfy_extras.nodes_upscale_model import ImageUpscaleWithModel
from signature_core.functional.transform import cutout
from signature_core.img.tensor_image import TensorImage
from signature_core.models.lama import Lama
from signature_core.models.salient_object_detection import SalientObjectDetection
from signature_core.models.seemore import SeeMore
from spandrel import ModelLoader

from nodes import SaveImage  # type: ignore

from .categories import MODELS_CAT


class MagicEraser(SaveImage):
    """Removes unwanted content from images using the Lama inpainting model.

    This class provides functionality to erase and reconstruct image regions based on a provided mask.
    The Lama model intelligently fills in the masked areas with contextually appropriate content.

    Args:
        image (torch.Tensor): Input image tensor in BWHC (Batch, Width, Height, Channel) format.
        mask (torch.Tensor): Binary mask tensor in BWHC format where 1 indicates areas to erase.
        preview (str): Controls preview image generation. Options:
            - "on": Saves preview images
            - "off": No preview images
        filename_prefix (str, optional): Prefix to use for saved output files. Defaults to "Signature".
        upscale_model (str, optional): Name of the upscale model to use. Defaults to None.
        prompt (str, optional): Text prompt for metadata. Defaults to None.
        extra_pnginfo (dict, optional): Additional metadata to save with output images. Defaults to None.

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing the processed image in BWHC format.

    Notes:
        - The model automatically handles memory cleanup after processing
        - Temporary files are saved with random suffixes to prevent naming conflicts
        - Preview images are saved at compression level 4 for balance of quality and size
    """

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + "".join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "preview": (["on", "off"],),
            },
            "optional": {
                "upscale_model": (["None"] + folder_paths.get_filename_list("upscale_models"),),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = MODELS_CAT

    def execute(self, **kwargs):
        image = kwargs.get("image")
        if not isinstance(image, torch.Tensor):
            raise ValueError("Image must be a torch.Tensor")

        mask = kwargs.get("mask")
        if not isinstance(mask, torch.Tensor):
            raise ValueError("Mask must be a torch.Tensor")

        preview = kwargs.get("preview", "off")
        if preview not in ["on", "off"]:
            raise ValueError("Preview must be 'on' or 'off'")

        upscale_model = kwargs.get("upscale_model", None)
        if upscale_model == "None":
            upscale_model = None

        upscale_fn = None
        loaded_upscale_model = None
        device = comfy.model_management.get_torch_device()
        if upscale_model is not None:
            upscale_model_path = folder_paths.get_full_path("upscale_models", upscale_model)
            sd = comfy.utils.load_torch_file(upscale_model_path, safe_load=True)
            if "module.layers.0.residual_group.blocks.0.norm1.weight" in sd:
                sd = comfy.utils.state_dict_prefix_replace(sd, {"module.": ""})
            loaded_upscale_model = ModelLoader().load_from_state_dict(sd)
            loaded_upscale_model.to(device)

            # TODO: See how we can unify this with the UpscaleImage node, probably it makes sense to extract the code
            # for the pure upscale into a function or class in signature-core
            upscaler = ImageUpscaleWithModel

            def upscale_image(image: torch.Tensor) -> torch.Tensor:
                return upscaler.upscale(upscaler, loaded_upscale_model, image)

            upscale_fn = upscale_image

        filename_prefix = kwargs.get("filename_prefix", "Signature")
        prompt = kwargs.get("prompt") or ""
        extra_pnginfo = kwargs.get("extra_pnginfo")

        model = Lama(device, upscale_fn)
        input_image = TensorImage.from_BWHC(image)
        input_mask = TensorImage.from_BWHC(mask)
        result = TensorImage(model.forward(input_image, input_mask), device=input_mask.device)

        output_images = TensorImage(result * (input_mask) + input_image * (1 - input_mask)).get_BWHC()
        if preview == "off":
            return (output_images,)
        result = self.save_images(output_images, filename_prefix, prompt, extra_pnginfo)
        result.update({"result": (output_images,)})

        model = None
        del model
        if loaded_upscale_model is not None:
            loaded_upscale_model = None
            del loaded_upscale_model

        return result


class Unblur(SaveImage):
    """Enhances image clarity by reducing blur using the SeeMore model.

    This class implements image deblurring functionality using the SeeMore neural network model.
    It's effective for correcting motion blur, out-of-focus areas, and general image softness.

    Args:
        image (torch.Tensor): Input image tensor in BWHC (Batch, Width, Height, Channel) format.
        preview (str): Controls preview image generation. Options:
            - "on": Saves preview images
            - "off": No preview images
        filename_prefix (str, optional): Prefix to use for saved output files. Defaults to "Signature".
        prompt (str, optional): Text prompt for metadata. Defaults to None.
        extra_pnginfo (dict, optional): Additional metadata to save with output images. Defaults to None.

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing the unblurred image in BWHC format.

    Notes:
        - The model automatically handles memory cleanup after processing
        - Temporary files are saved with random suffixes to prevent naming conflicts
        - Preview images are saved at compression level 4 for balance of quality and size
    """

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + "".join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
                "preview": (["on", "off"],),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = MODELS_CAT

    def execute(self, **kwargs):
        image = kwargs.get("image")
        if not isinstance(image, torch.Tensor):
            raise ValueError("Image must be a torch.Tensor")

        preview = kwargs.get("preview")
        if preview not in ["on", "off"]:
            raise ValueError("Preview must be either 'on' or 'off'")

        filename_prefix = kwargs.get("filename_prefix", "Signature")
        prompt = kwargs.get("prompt")
        extra_pnginfo = kwargs.get("extra_pnginfo")
        model = SeeMore()
        input_image = TensorImage.from_BWHC(image)
        output_image = model.forward(input_image)
        output_images = TensorImage(output_image).get_BWHC()

        if preview == "off":
            return (output_images,)
        result = self.save_images(output_images, filename_prefix, prompt, extra_pnginfo)
        result.update({"result": (output_images,)})
        model = None
        del model
        return result


class BackgroundRemoval(SaveImage):
    """Separates foreground subjects from image backgrounds using AI segmentation models.

    This class provides multiple AI models for background removal, offering different approaches and
    quality levels for various use cases. It can output both masked and RGBA versions of the results.

    Args:
        image (torch.Tensor): Input image tensor in BWHC (Batch, Width, Height, Channel) format.
        model_name (str): The AI model to use for segmentation. Options:
            - "inspyrenet": General-purpose segmentation
            - "rmbg14": Optimized for human subjects
            - "isnet_general": Balanced approach for various subjects
            - "fakepng": Fast but lower quality option
        preview (str): Controls preview output type. Options:
            - "mask": Shows the segmentation mask
            - "rgba": Shows the transparent background result
            - "none": No preview
        filename_prefix (str, optional): Prefix to use for saved output files. Defaults to "Signature".
        prompt (str, optional): Text prompt for metadata. Defaults to None.
        extra_pnginfo (dict, optional): Additional metadata to save with output images. Defaults to None.

    Returns:
        tuple[torch.Tensor, torch.Tensor, torch.Tensor]: A tuple containing:
            - rgba: Image with transparent background in BWHC format
            - rgb: Original image with background in BWHC format
            - mask: Binary segmentation mask in BWHC format

    Notes:
        - The model automatically handles memory cleanup after processing
        - Temporary files are saved with random suffixes to prevent naming conflicts
        - Preview images are saved at compression level 4 for balance of quality and size
        - Different models may perform better on different types of images
    """

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + "".join(random.choice("abcdefghijklmnopqrstupvxyz") for _ in range(5))
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "model_name": (["inspyrenet", "rmbg14", "isnet_general", "fakepng"],),
                "preview": (["mask", "rgba", "none"],),
                "image": ("IMAGE",),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "MASK")
    RETURN_NAMES = ("rgba", "rgb", "mask")
    FUNCTION = "execute"
    CATEGORY = MODELS_CAT

    def execute(self, **kwargs):
        image = kwargs.get("image")
        if not isinstance(image, torch.Tensor):
            raise ValueError("Image must be a torch.Tensor")

        model_name = kwargs.get("model_name")
        if not isinstance(model_name, str):
            raise ValueError("Model name must be a string")
        if model_name not in ["inspyrenet", "rmbg14", "isnet_general", "fakepng"]:
            raise ValueError("Invalid model name")

        preview = kwargs.get("preview")
        if not isinstance(preview, str):
            raise ValueError("Preview must be a string")
        if preview not in ["mask", "rgba", "none"]:
            raise ValueError("Invalid preview type")

        filename_prefix = kwargs.get("filename_prefix", "Signature")
        if not isinstance(filename_prefix, str):
            raise ValueError("Filename prefix must be a string")

        prompt = kwargs.get("prompt")
        extra_pnginfo = kwargs.get("extra_pnginfo")

        model = SalientObjectDetection(model_name=model_name)
        input_image = TensorImage.from_BWHC(image)
        masks = model.forward(input_image)

        output_masks = TensorImage(masks)
        rgb, rgba = cutout(input_image, output_masks)
        rgb_output = TensorImage(rgb).get_BWHC()
        rgba_output = TensorImage(rgba).get_BWHC()
        mask_output = output_masks.get_BWHC()
        if preview == "none":
            return (
                rgba_output,
                rgb_output,
                mask_output,
            )
        preview_images = output_masks.get_rgb_or_rgba().get_BWHC() if preview == "mask" else rgba_output
        result = self.save_images(preview_images, filename_prefix, prompt, extra_pnginfo)
        result.update(
            {
                "result": (
                    rgba_output,
                    rgb_output,
                    mask_output,
                )
            }
        )
        model = None
        del model
        return result
