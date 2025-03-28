from neurochain.dojo.create_training_run import (
    CreateTrainingRun as CreateTrainingRunNeurochain,
)

from ...categories import DOJO_CAT


class CreateTrainingRun:
    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "dataset_path": ("STRING", {"default": ""}),
                "config": ("STRING", {"multiline": True}),
                "model_name": ("STRING", {"default": "default_model_name"}),
                "description": ("STRING", {"multiline": True}),
                "model_type": (["loras", "flux_lora", "lora"],),
                "config_type": (["toml", "yaml", "json"],),
                "org_id": (
                    "STRING",
                    {"default": ""},
                ),
                "user_id": (
                    "STRING",
                    {"default": ""},
                ),
                "license_id": (
                    "STRING",
                    {"default": "019377ae-49e2-7dc3-b130-44c064569ef0"},
                ),
                "s3_bucket_name": (
                    "STRING",
                    {"default": "signature-trainings"},
                ),
                "api_host": ("STRING", {"default": ""}),
                "backend_cognito_secret_name": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = (
        "STRING",
        "STRING",
        "STRING",
        "STRING",
    )
    RETURN_NAMES = ("model_id", "user_id", "org_id", "s3_bucket_name")
    FUNCTION = "process"
    CATEGORY = DOJO_CAT
    OUTPUT_NODE = True

    def process(
        self,
        dataset_path: str,
        config: str,
        model_name: str,
        description: str,
        model_type: str,
        config_type: str,
        org_id: str,
        user_id: str,
        license_id: str,
        s3_bucket_name: str,
        api_host: str,
        backend_cognito_secret_name: str,
    ):
        return CreateTrainingRunNeurochain.create_flux_training(
            dataset_path=dataset_path,
            config=config,
            model_name=model_name,
            description=description,
            model_type=model_type,
            config_type=config_type,
            org_id=org_id,
            user_id=user_id,
            license_id=license_id,
            s3_bucket_name=s3_bucket_name,
            api_host=api_host,
            backend_cognito_secret_name=backend_cognito_secret_name,
        )
