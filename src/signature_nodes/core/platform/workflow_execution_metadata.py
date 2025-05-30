import json

from uuid_extensions import uuid7str

from ...categories import PLATFORM_IO_CAT
from ...shared import settings


class WorkflowExecutionMetadata:
    """
    Extracts platform execution metadata from a JSON string.

    This node parses a JSON string to extract platform execution metadata
    including backend API host, generate service host, organisation ID,
    and client ID.

    Parameters:
        json_str (str): A JSON string containing platform execution metadata.

    Returns:
        tuple[str, str, str, str]: A tuple containing the extracted metadata values.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "hidden": {
                "json_str": (
                    "STRING",
                    {
                        "default": "{}",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "backend_api_host",
        "generate_service_host",
        "organisation_id",
        "user_id",
        "environment",
        "workflow_id",
        "backend_cognito_secret",
        "runpod_endpoint_id",
    )
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT
    DESCRIPTION = """
    Extracts platform execution metadata from a JSON string.
    Parses a JSON string to extract platform execution metadata
    including backend API host, generate service host, organisation ID,
    and client ID.
    """

    def execute(self, json_str: str) -> tuple[str, str, str, str, str, str, str, str]:
        json_dict = json.loads(json_str)
        settings.correlation_id = json_dict.get("correlation_id", uuid7str())

        return (
            json_dict.get("backend_api_host", ""),
            json_dict.get("generate_service_host", ""),
            json_dict.get("organisation_id", ""),
            json_dict.get("user_id", ""),
            json_dict.get("environment", ""),
            json_dict.get("workflow_id", ""),
            json_dict.get("backend_cognito_secret", ""),
            json_dict.get("runpod_endpoint_id", ""),
        )
