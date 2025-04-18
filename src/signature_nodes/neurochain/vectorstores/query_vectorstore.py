import boto3
import requests
from neurochain.utils.utils import get_secret, query_vectorstore

from ...categories import VECTORSTORE_CAT
from ...env import env


class QueryVectorstore:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "tenant_id": ("STRING", {"default": "test"}),
                "k": ("INT", {"default": 3, "min": 1}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("results",)
    FUNCTION = "process"
    CATEGORY = VECTORSTORE_CAT
    OUTPUT_NODE = True

    def process(self, prompt: str, tenant_id: str, k: int = 3):
        environment = env.get("ENVIRONMENT")
        host = f"https://signature-generate.signature-eks-{environment}.signature.ai"

        session = boto3.Session()
        backend_cognito_secret = get_secret(session, env.get("BACKEND_COGNITO_SECRET"))
        if backend_cognito_secret is None:
            raise ValueError("Backend Cognito Secret not found")

        client_id = backend_cognito_secret["client_id"]
        client_secret = backend_cognito_secret["client_secret"]
        client_scope = backend_cognito_secret["scope"]
        cognito_response = requests.post(
            backend_cognito_secret["cognito_oauth_url"],
            data=f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}&scope={client_scope}/read",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = cognito_response.json()["access_token"]

        response = query_vectorstore(query=prompt, k=k, tenant_id=tenant_id, token=token, host=host).json()
        results = response["results"][0]["results"]
        return (results,)
