import os

import boto3
import requests
from neurochain.utils.utils import make_upsert_request

from ...categories import VECTORSTORE_CAT
from ..utils import get_secret


class UploadToVectorstore:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tenant_id": ("STRING", {"default": "test"}),
                "chunks": ("CHUNKS", {}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "process"
    CATEGORY = VECTORSTORE_CAT
    OUTPUT_NODE = True

    def process(self, tenant_id: str, chunks):
        environment = os.environ.get("ENVIRONMENT", "staging")
        host = f"https://signature-generate.signature-eks-{environment}.signature.ai"

        session = boto3.Session()
        backend_cognito_secret = get_secret(
            session,
            os.environ.get("BACKEND_COGNITO_SECRET", f"{environment}_backend_cognito_oauth"),
        )
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

        response = make_upsert_request(tenant_id=tenant_id, token=token, host=host, chunks=chunks)
        return (response.text,)
