from neurochain.utils.utils import get_signature_models

from ...categories import STORAGE_CAT


class GetSignatureModels:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "org_id": ("STRING", {"default": "66310e12f6ce596d498cb975"}),
                "token": ("STRING", {"default": ""}),
                "host": ("STRING", {"default": "https://etudes.signature.ai"}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("models",)
    FUNCTION = "process"
    CATEGORY = STORAGE_CAT
    OUTPUT_NODE = True

    def process(self, org_id: str, token: str, host: str):
        response = get_signature_models(organisation_id=org_id, token=token, host=host)
        return (response.json(),)
