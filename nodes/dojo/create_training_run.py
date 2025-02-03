import json
import os
import shutil

import boto3
import requests

from ..categories import DOJO_CAT
from ..shared import get_secret
from .utils import upload_folder, write_to_toml, write_to_yaml


class CreateTrainingRun:
    @classmethod
    def INPUT_TYPES(cls):
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
        print(f"Starting training run creation for model: {model_name}")
        environment = os.environ.get("ENVIRONMENT", "staging")
        host = f"https://signature-api.signature-eks-{environment}.signature.ai"
        print(f"Using API endpoint: {host}")

        ## 1. generate cognito token
        print("Generating Cognito token...")
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
        print("Successfully obtained Cognito token")

        ## 2. create the model
        print(f"Creating model '{model_name}' of type '{model_type}'...")
        url = f"{host}/api/v1_restricted/model"

        headers = {
            "accept": "application/json",
            "authorization": "Bearer {}".format(cognito_response.json()["access_token"]),
            "X-Organisation-Uuid": org_id,
            "X-User-Uuid": user_id,
        }

        model_data = {
            "name": model_name,
            "description": description,
            "modelUrl": f"https://{model_name}.com",
            "modelType": model_type,
            "metadata": json.dumps({"key": "value"}),
            "licenseUuid": license_id,
        }

        response = requests.post(url, headers=headers, json=model_data)
        if not response.ok:
            print(f"Error creating model: {response.status_code} - {response.text}")
            raise Exception(f"Failed to create model: {response.text}")
        print(f"Successfully created model with ID: {response.json()['result']['uuid']}")

        ## 2. Create the model S3 path, and update the model
        model_id = response.json()["result"]["uuid"]
        model_version = response.json()["result"]["version"]
        print(f"Updating model {model_id} version {model_version}...")
        s3_model_url = f"s3://{s3_bucket_name}/{model_id}/{model_version}/{model_id}_{model_version}.safetensors"

        url = f"{host}/api/v1_restricted/model/{model_id}/version/{model_version}"
        data = {
            "name": model_name,
            "description": description,
            "modelUrl": s3_model_url,
            "modelType": model_type,
            "metadata": json.dumps({"key": "value"}),
            "licenseUuid": license_id,
        }

        response = requests.put(url, json=data, headers=headers)
        if not response.ok:
            print(f"Error updating model: {response.status_code} - {response.text}")
            raise Exception(f"Failed to update model: {response.text}")
        print("Successfully updated model")

        ## activate model - models are "in development" by default
        print("Activating model...")
        url = f"{host}/api/v1_restricted/model/{model_id}/version/{model_version}/release"
        data = {"release": "active"}
        release_response = requests.put(url, json=data, headers=headers)
        if not release_response.ok:
            print(f"Error activating model: {release_response.status_code} - {release_response.text}")
            raise Exception(f"Failed to activate model: {release_response.text}")
        print("Successfully activated model")

        train_session_payload_path = f"/tmp/{model_id}"  # nosec

        if os.path.exists(train_session_payload_path):
            shutil.rmtree(train_session_payload_path)
        os.makedirs(train_session_payload_path, exist_ok=True)

        if config_type == "toml":
            write_to_toml(
                content=config,
                file_path=os.path.join(train_session_payload_path, "config.toml"),
            )
        else:
            write_to_yaml(
                content=config,
                file_path=os.path.join(train_session_payload_path, "config.yaml"),
            )
        shutil.move(dataset_path, os.path.join(train_session_payload_path, "dataset"))
        print(os.path.join(train_session_payload_path, "dataset"))

        print(f"Preparing training session payload at {train_session_payload_path}...")
        print(f"Uploading training session payload to S3 bucket: {s3_bucket_name}")
        upload_folder(
            local_dir=train_session_payload_path,
            s3_bucket=s3_bucket_name,
            s3_folder=f"{model_id}/{model_version}",
        )
        print("Successfully uploaded training session payload")

        print(f"Training run creation completed for model: {model_name}")
        return (model_id, model_version, user_id, org_id, s3_bucket_name)
