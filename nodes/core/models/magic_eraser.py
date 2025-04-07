import random

import comfy.model_management  # type: ignore
import folder_paths  # type: ignore
import torch
from comfy_extras.nodes_upscale_model import ImageUpscaleWithModel  # type: ignore
from signature_core.img.tensor_image import TensorImage
from signature_core.models.lama import Lama
from spandrel import ModelLoader

from nodes import SaveImage  # type: ignore

from ...categories import MODELS_CAT


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
    DESCRIPTION = """
    Removes unwanted content from images using the Lama inpainting model.
    Intelligently fills in masked areas with contextually appropriate content.
    Supports optional upscaling for higher quality results.
    """

    def execute(
        self,
        image: torch.Tensor,
        mask: torch.Tensor,
        preview: str,
        upscale_model: str | None,
        extra_pnginfo: dict,
        prompt: str = "",
    ):
        upscale_fn = None
        loaded_upscale_model = None
        device = comfy.model_management.get_torch_device()
        if upscale_model is not None and upscale_model != "None":
            print("upscale_model", upscale_model)
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

        filename_prefix = "Signature"

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
