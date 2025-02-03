import json
import logging
import os

BASE_COMFY_DIR = os.path.dirname(os.path.realpath(__file__)).split("custom_nodes")[0]
COMFY_IMAGES_DIR = os.path.join(BASE_COMFY_DIR, "input")

logger = logging.getLogger(__name__)


def get_secret(session, secret_name, region_name="eu-west-1"):
    client = session.client(service_name="secretsmanager", region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            return json.loads(response["SecretString"])
    except Exception as e:
        print(f"Error getting secret: {e}")
        raise
