from pathlib import Path

import requests
from uuid_extensions import uuid7str

from ....categories import S3_CAT


class UploadToS3:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "host": ("STRING", {"default": "https://api.signature.ai"}),
            },
            "optional": {
                "file_bytes_list": ("LIST", {"default": None}),
                "file_paths": ("LIST", {"default": None}),
            },
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("s3_ids",)
    FUNCTION = "process"
    CATEGORY = S3_CAT
    OUTPUT_NODE = True

    def process(self, host: str, file_bytes_list: list | None = None, file_paths: list | None = None):
        url = f"{host}/api/v1/assets/upload-file-to-s3"
        headers = {"accept": "application/json"}

        uploaded_files = []

        if file_bytes_list:
            for f_bytes in file_bytes_list:
                s3_file_id = uuid7str()
                params = {"id": s3_file_id}
                files = {"file": (f_bytes)}
                response = requests.post(url, params=params, files=files, headers=headers)
                if response.status_code == 200:
                    uploaded_files.append(s3_file_id)

        if file_paths:
            for file_path in file_paths:
                with open(file_path, "rb") as f:
                    s3_file_id = f"{uuid7str()}_{Path(file_path).name}"
                    params = {"id": s3_file_id}
                    files = {"file": (f.read())}
                    response = requests.post(url, params=params, files=files, headers=headers)
                    if response.status_code == 200:
                        uploaded_files.append(s3_file_id)

        return (uploaded_files,)
