import os

import boto3
import requests

from ..categories import DOJO_CAT


class StartTrainingRun:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_id": ("STRING", {"default": ""}),
                "model_version": ("STRING", {"default": ""}),
                "org_id": (
                    "STRING",
                    {"default": "66310e12f6ce596d498cb975"},
                ),
                "user_id": (
                    "STRING",
                    {"default": ""},
                ),
                "is_flux": ("BOOLEAN", {"default": True}),
                "s3_bucket_name": (
                    "STRING",
                    {"default": "signature-trainings"},
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("train_id",)
    FUNCTION = "process"
    CATEGORY = DOJO_CAT
    OUTPUT_NODE = True

    def process(
        self,
        model_id: str,
        model_version: str,
        org_id: str,
        user_id: str,
        is_flux: bool,
        s3_bucket_name: str,
    ):
        environment = os.environ.get("ENVIRONMENT", "staging")

        if is_flux:
            secret_name = f"signature-ml-{environment}-api-secret-key"
            train_endpoint = (
                "https://ml-platform.signature.ai/batch_train"
                if environment == "production"
                else f"https://ml-platform.{environment}.signature.ai/batch_train"
            )

            ## trigger training on ML Platform
            secretsmanager_client = boto3.client("secretsmanager")
            secret_value = secretsmanager_client.get_secret_value(SecretId=secret_name)
            api_key = secret_value["SecretString"]

            headers = {
                "Accept": "*/*",
                "X-Api-Key": api_key,
                "Content-Type": "application/json",
            }

            data = {
                "user_id": user_id,
                "organisation_id": org_id,
                "model_id": model_id,
                "model_path": f"s3://{s3_bucket_name}/{model_id}/{model_version}",
                "model_name": f"{model_id}_{model_version}",
                "model_version": model_version,
                "instance_type": "g5.4xlarge",
            }

            response = requests.post(train_endpoint, headers=headers, json=data)
            print(response.text)
            return (response.text,)
        else:
            return ("no training launched - specify 'is_flux'",)
