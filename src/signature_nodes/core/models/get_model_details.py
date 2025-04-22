import json

import boto3
import requests

from ...categories import PLATFORM_IO_CAT


class GetModelDetails:
    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "model_uuid": ("STRING", {"forceInput": True}),
                "version_uuid": ("STRING", {"forceInput": True}),
                "backend_api_host": ("STRING", {"forceInput": True}),
                "backend_coginto_secret": ("STRING", {"forceInput": True}),
                "user_id": ("STRING", {"forceInput": True}),
                "org_id": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("model_details",)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT
    DESCRIPTION = """Get the model details from the backend"""

    def execute(self, model_uuid, version_uuid, backend_api_host, backend_coginto_secret, user_id, org_id):
        # Move this to core in the future
        def get_secret(session, secret_name, region_name="eu-west-1"):
            client = session.client(service_name="secretsmanager", region_name=region_name)
            try:
                response = client.get_secret_value(SecretId=secret_name)
                if "SecretString" in response:
                    return json.loads(response["SecretString"])
            except Exception as e:
                print(f"Error getting secret: {e}")
                raise

        session = boto3.Session()
        backend_cognito_secret = get_secret(session, backend_coginto_secret)
        if backend_cognito_secret is None:
            raise Exception(f"Backend Cognito Secret with name {backend_coginto_secret} is not found")

        client_id = backend_cognito_secret["client_id"]
        client_secret = backend_cognito_secret["client_secret"]
        client_scope = backend_cognito_secret["scope"]
        cognito_response = requests.post(
            backend_cognito_secret["cognito_oauth_url"],
            data=f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}&scope={client_scope}/read",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        headers = {
            "accept": "application/json",
            "authorization": "Bearer {}".format(cognito_response.json()["access_token"]),
            "X-User-Uuid": user_id,
            "X-Organisation-Uuid": org_id,
        }

        response = requests.get(
            f"{backend_api_host}/api/v1_restricted/model/{model_uuid}/version/{version_uuid}",
            headers=headers,
        )

        if response.status_code != 200:
            raise Exception(f"Error getting model url: {response.status_code}, {response}")
        return (response.json(),)
