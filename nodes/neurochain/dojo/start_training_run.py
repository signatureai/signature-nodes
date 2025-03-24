from neurochain.dojo.start_training_run import StartTrainingRun as StartTrainingRunNeurochain

from ...categories import DOJO_CAT


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
                "training_type": (["aitoolkit", "simpletuner"], {"default": "aitoolkit"}),
                "backend_api": ("STRING", {"default": "https://signature-api.signature-eks-staging.signature.ai"}),
                "backend_api_secret_name": ("STRING", {"default": "staging_backend_cognito_oauth"}),
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
        training_type: str,
        backend_api: str,
        backend_api_secret_name: str,
    ):
        if is_flux:
            training_id = StartTrainingRunNeurochain().start_flux_training(
                model_id,
                model_version,
                org_id,
                user_id,
                s3_bucket_name,
                training_type,
                backend_api,
                backend_api_secret_name,
            )
            print(training_id)
            return (training_id,)
        else:
            return ("no training launched - specify 'is_flux'",)
