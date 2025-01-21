import os
from typing import Optional, Tuple

import comfy.model_management
import folder_paths  # type: ignore
import torch
from neurochain.agents.florence2 import Florence2 as Florence2Neurochain
from signature_core.img.tensor_image import TensorImage

from ....categories import AGENT_CAT
from ...florence_utils import FLORENCE_PROCESSORS

SIG_MODELS_DIR = "sig_models"


class Florence2:
    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "local_model": ("BOOLEAN", {"default": False}),
                "endpoint_name": (
                    "STRING",
                    {"default": "Florence-2-large"},
                ),
                "infer_endpoint": (
                    "STRING",
                    {"default": "https://ml-platform-inference.signature.ai/invoke_model"},
                ),
                "image": ("IMAGE",),
                "task_token": (
                    [
                        "<CAPTION>",
                        "<DETAILED_CAPTION>",
                        "<MORE_DETAILED_CAPTION>",
                        "<OD>",
                        "<DENSE_REGION_CAPTION>",
                        "<REGION_PROPOSAL>",
                        "<CAPTION_TO_PHRASE_GROUNDING>",
                        "<REFERRING_EXPRESSION_SEGMENTATION>",
                        "<REGION_TO_SEGMENTATION>",
                        "<OPEN_VOCABULARY_DETECTION>",
                        "<REGION_TO_CATEGORY>",
                        "<REGION_TO_DESCRIPTION>",
                        "<OCR>",
                        "<OCR_WITH_REGION>",
                    ],
                ),
                "num_beams": ("INT", {"default": 3, "min": 1, "max": 50}),
                "attention": (["sdpa", "flash_attention_2", "eager"], {"default": "sdpa"}),
                "precision": (["float16", "bfloat16", "float32"], {"default": "float16"}),
            },
            "optional": {
                "text_prompt": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "response")
    FUNCTION = "process"
    CATEGORY = AGENT_CAT
    OUTPUT_NODE = True

    def process(
        self,
        local_model: bool,
        endpoint_name: str,
        infer_endpoint: str,
        image: torch.Tensor,
        task_token: str,
        num_beams: int,
        attention: str,
        precision: str,
        text_prompt: Optional[str] = None,
    ):
        base_model_path = None
        if local_model:
            base_model_path = os.path.join(folder_paths.models_dir, SIG_MODELS_DIR)
            if not os.path.exists(base_model_path):
                os.makedirs(base_model_path)

        tensor_img = TensorImage.from_BWHC(data=image)
        base64_string = tensor_img.get_base64()

        if text_prompt == "undefined" or text_prompt == "":
            text_prompt = None

        device = comfy.model_management.get_torch_device()
        florence2 = Florence2Neurochain(endpoint_name, infer_endpoint, base_model_path, device, attention, precision)
        raw_task_resp = florence2.generate(base64_string, task_token, text_prompt, num_beams)

        final_resp: Tuple[Optional[torch.Tensor], Optional[torch.Tensor], str] = (
            image,
            image,
            raw_task_resp,
        )

        for task_processor in FLORENCE_PROCESSORS:
            if task_token in task_processor.task_tokens:
                final_resp = task_processor.process_output(
                    input_img=image, text_prompt=text_prompt, raw_output=raw_task_resp
                )
                break

        return final_resp
