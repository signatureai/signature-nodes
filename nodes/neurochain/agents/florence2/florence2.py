import json
from typing import Optional, Tuple

import boto3
import requests
import torch
from signature_core.img.tensor_image import TensorImage

from ....categories import AGENT_CAT
from ...florence_utils import FLORENCE_PROCESSORS
from ...utils import get_async_output


class Florence2:
    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "endpoint_name": (
                    "STRING",
                    {"default": "Florence-2-large-10-11-2024-15-59-19-endpoint"},
                ),
                "infer_endpoint": (
                    "STRING",
                    {"default": "https://d9w8eb8b1b.execute-api.eu-west-1.amazonaws.com/development/invoke_model"},
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
        endpoint_name: str,
        infer_endpoint: str,
        task_token: str,
        image: torch.Tensor,
        num_beams: int,
        text_prompt: Optional[str] = None,
    ):
        tensor_img = TensorImage.from_BWHC(data=image)
        base64_string = tensor_img.get_base64()

        inputs: dict[str, Optional[str]] = {
            "task_token": task_token,
            "image_b64": base64_string,
        }

        if text_prompt == "undefined" or text_prompt == "":
            text_prompt = None

        inputs["text_prompt"] = text_prompt

        secret_name = "signature-ml-development-models-api-secret-key"  # nosec
        secretsmanager_client = boto3.client("secretsmanager")
        secret_value = secretsmanager_client.get_secret_value(SecretId=secret_name)
        model_api_key = secret_value["SecretString"]

        headersList = {
            "Accept": "*/*",
            "X-Api-Key": model_api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "endpoint_name": endpoint_name,
            "parameters": {"max_new_tokens": 1024, "num_beams": num_beams},
            "inputs": inputs,
        }
        payload = json.dumps(payload)

        infer_req_response = requests.request("POST", infer_endpoint, data=payload, headers=headersList).json()

        response = get_async_output(infer_req_response["output_location"])
        response_json = json.loads(response)
        raw_task_resp = response_json[task_token]
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
