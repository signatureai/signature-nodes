from neurochain.dojo.create_training_run import (
    CreateTrainingRun as CreateTrainingRunNeurochain,
)

from ..categories import DOJO_CAT


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
                "config_type": (["toml", "yaml"],),
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
            }
        }

    RETURN_TYPES = (
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
    )
    RETURN_NAMES = ("model_id", "model_version", "user_id", "org_id", "s3_bucket_name")
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
    ):
        return CreateTrainingRunNeurochain(
            dataset_path,
            config,
            model_name,
            description,
            model_type,
            config_type,
            org_id,
            user_id,
            license_id,
            s3_bucket_name,
        )
