import os

import boto3
import requests
from neurochain.utils.utils import get_secret

from .....env import env
from ....categories import S3_CAT
from ...utils import COMFY_IMAGES_DIR


class DownloadFromS3:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_name": ("STRING", {"default": ""}),
                "prefix": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("FILE",)
    RETURN_NAMES = ("file",)
    FUNCTION = "process"
    CATEGORY = S3_CAT
    OUTPUT_NODE = True

    def process(self, file_name: str, prefix: str):
        environment = env.get("ENVIRONMENT")
        host = f"https://signature-generate.signature-eks-{environment}.signature.ai"

        session = boto3.Session()
        backend_cognito_secret = get_secret(
            session,
            env.get("BACKEND_COGNITO_SECRET"),
        )
        if not backend_cognito_secret:
            raise ValueError("Back-end Cognito Secret not found")

        client_id = backend_cognito_secret["client_id"]
        client_secret = backend_cognito_secret["client_secret"]
        client_scope = backend_cognito_secret["scope"]
        cognito_response = requests.post(
            backend_cognito_secret["cognito_oauth_url"],
            data=f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}&scope={client_scope}/read",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = cognito_response.json()["access_token"]

        url = f"{host}/api/v1/assets/download"
        params = {"file_name": file_name, "prefix": prefix}
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        file_path = os.path.join(COMFY_IMAGES_DIR, file_name)

        output = [{"name": file_path, "type": "image/png"}]
        if not os.path.isfile(file_path):
            response = requests.get(url, params=params, headers=headers)

            if response.status_code == 200:
                file_bytes = response.content

                if file_bytes and not os.path.isfile(file_path):
                    with open(file_path, "wb") as f:
                        f.write(file_bytes)

            else:
                print(f"Error downloading file: {response.status_code}")
                return ([],)
        return (output,)
