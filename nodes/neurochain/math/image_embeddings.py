import json

import boto3
import requests
import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import MATH_CAT
from ..utils import get_async_output


class ImageEmbeddings:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "endpoint_name": ("STRING", {"default": "Resnet50Embeddings-10-02-2024-16-24-45-endpoint"}),
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("embeddings",)
    FUNCTION = "process"
    CATEGORY = MATH_CAT
    OUTPUT_NODE = True

    def process(self, endpoint_name: str, image: torch.Tensor):
        tensor_img = TensorImage.from_BWHC(data=image)
        base64_string = tensor_img.get_base64()

        secret_name = "signature-ml-development-models-api-secret-key"
        secretsmanager_client = boto3.client("secretsmanager")
        secret_value = secretsmanager_client.get_secret_value(SecretId=secret_name)
        model_api_key = secret_value["SecretString"]

        reqUrl = "https://ei2ybimz5h.execute-api.eu-west-1.amazonaws.com/development/invoke"
        headersList = {"Accept": "*/*", "X-Api-Key": model_api_key, "Content-Type": "application/json"}

        payload = {"endpoint_name": endpoint_name, "inputs": {"image_b64": base64_string}}
        payload = json.dumps(payload)

        infer_req_response = requests.request("POST", reqUrl, data=payload, headers=headersList).json()

        response = get_async_output(infer_req_response["output_location"])
        response_json = json.loads(response)
        output = response_json["response"]
        return (output,)
