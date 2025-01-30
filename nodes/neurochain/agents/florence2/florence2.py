import os
from typing import Optional, Tuple

import comfy.model_management  # type: ignore
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
                "image": ("IMAGE",),
                "task_token": (
                    [
                        "CAPTION",  # 1
                        "DETAILED_CAPTION",  # 1
                        "MORE_DETAILED_CAPTION",  # 1
                        "OD",  # 4
                        "DENSE_REGION_CAPTION",  # 4
                        "REGION_PROPOSAL",  # 4
                        "CAPTION_TO_PHRASE_GROUNDING",  # 2
                        "REFERRING_EXPRESSION_SEGMENTATION",  # 3
                        "REGION_TO_SEGMENTATION",
                        "OPEN_VOCABULARY_DETECTION",  # 2
                        "REGION_TO_CATEGORY",
                        "REGION_TO_DESCRIPTION",
                        "OCR",  # 1
                        "OCR_WITH_REGION",  # 2
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

    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "STRING")
    RETURN_NAMES = ("image", "mask", "caption", "data")
    FUNCTION = "process"
    CATEGORY = AGENT_CAT
    OUTPUT_NODE = True

    def process(
        self,
        image: torch.Tensor,
        task_token: str,
        num_beams: int,
        attention: str,
        precision: str,
        text_prompt: Optional[str] = None,
    ):
        base_model_path = None
        base_model_path = os.path.join(folder_paths.models_dir, SIG_MODELS_DIR)
        if not os.path.exists(base_model_path):
            os.makedirs(base_model_path)

        tensor_img = TensorImage.from_BWHC(data=image)
        base64_string = tensor_img.get_base64()

        if text_prompt == "undefined" or text_prompt == "":
            text_prompt = None

        device = comfy.model_management.get_torch_device()
        florence2 = Florence2Neurochain(base_model_path, device, attention, precision)
        raw_task_resp = florence2.generate(base64_string, f"<{task_token}>", text_prompt, num_beams)

        final_resp: Tuple[Optional[torch.Tensor], Optional[torch.Tensor], dict, str]
        if isinstance(raw_task_resp, str):
            final_resp = (
                image,
                image,
                {},
                raw_task_resp,
            )
        else:
            final_resp: Tuple[Optional[torch.Tensor], Optional[torch.Tensor], dict, str] = (
                image,
                image,
                raw_task_resp,
                "",
            )

        for task_processor in FLORENCE_PROCESSORS:
            if f"<{task_token}>" in task_processor.task_tokens:
                final_resp = task_processor.process_output(
                    input_img=image, text_prompt=text_prompt, raw_output=raw_task_resp
                )
                break

        return final_resp
