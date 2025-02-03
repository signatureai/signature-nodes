import os

import boto3
import yaml
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")


def upload_file(s3_client, local_path, s3_bucket, s3_path):
    """
    uploads a single file
    """
    try:
        s3_client.upload_file(local_path, s3_bucket, s3_path)
        print(s3_bucket)
        print(f"Uploaded file {local_path} to {s3_bucket}/{s3_path}")
        return True
    except ClientError as e:
        print(f"Error uploading file: {e}")
        return False


def upload_folder(local_dir: str, s3_bucket: str, s3_folder: str):
    """
    uploads a folder to s3
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_dir)
            s3_path = os.path.join(s3_folder, relative_path).replace("\\", "/")
            upload_file(s3_client, local_path, s3_bucket, s3_path)


def write_to_toml(content, file_path):
    """
    Write content to a TOML file.

    :param content: A dictionary containing the data to be written to the TOML file
    :param file_path: The path where the TOML file should be created or updated
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as toml_file:
        toml_file.write(content)

    print(f"Content has been written to {file_path}")


def write_to_yaml(content, file_path):
    """
    Write content to a YAML file.

    :param content: A dictionary containing the data to be written to the YAML file
    :param file_path: The path where the YAML file should be created or updated
    """
    content = yaml.safe_load(content)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as yaml_file:
        yaml.dump(content, yaml_file, default_flow_style=False)

    print(f"Content has been written to {file_path}")


if __name__ == "__main__":
    pass
