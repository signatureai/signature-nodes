from neurochain.dojo.start_training_run import StartTrainingRun as StartTrainingRunNeurochain

from ...categories import DOJO_CAT
from ...shared import settings


class StartTrainingRun:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_id": ("STRING", {"default": ""}),
                "org_id": (
                    "STRING",
                    {"default": "66310e12f6ce596d498cb975"},
                ),
                "user_id": (
                    "STRING",
                    {"default": ""},
                ),
                "s3_bucket_name": (
                    "STRING",
                    {"default": "signature-trainings"},
                ),
                "training_target": (["runpod", "batch"], {"default": "runpod"}),
                "runpod_endpoint_id": ("STRING", {"default": "4zl0zcg2r1alpi"}),
                "backend_api": ("STRING", {"default": "https://signature-api.signature-eks-staging.signature.ai"}),
                "backend_api_secret_name": ("STRING", {"default": "staging_backend_cognito_oauth"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("return_message",)
    FUNCTION = "process"
    CATEGORY = DOJO_CAT
    OUTPUT_NODE = True

    def process(
        self,
        model_id: str,
        org_id: str,
        user_id: str,
        s3_bucket_name: str,
        training_target: str,
        runpod_endpoint_id: str,
        backend_api: str,
        backend_api_secret_name: str,
    ):
        return_message = StartTrainingRunNeurochain().start_flux_training(
            model_id,
            org_id,
            user_id,
            s3_bucket_name,
            training_target,
            runpod_endpoint_id,
            backend_api,
            backend_api_secret_name,
            settings.correlation_id,
        )
        return (return_message,)
