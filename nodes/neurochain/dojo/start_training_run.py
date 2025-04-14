from neurochain.dojo.start_training_run import StartTrainingRun as StartTrainingRunNeurochain

from ...categories import DOJO_CAT


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
        org_id: str,
        user_id: str,
        s3_bucket_name: str,
        training_target: str,
        backend_api: str,
        backend_api_secret_name: str,
    ):
        training_id = StartTrainingRunNeurochain().start_flux_training(
            model_id,
            org_id,
            user_id,
            s3_bucket_name,
            training_target,
            backend_api,
            backend_api_secret_name,
        )
        print(training_id)
        return (training_id,)
