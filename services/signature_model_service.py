import logging
import os
import sys
import traceback

import boto3
from aiohttp import web
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from .. import BASE_COMFY_DIR

sys.path.append(BASE_COMFY_DIR)
import folder_paths  # type: ignore # noqa: E402
from server import PromptServer  # type: ignore # noqa: E402

current_dir = os.getcwd()
sys.path.append(current_dir)

# Load environment variables
load_dotenv()


class SignatureModelService:
    @classmethod
    def setup_routes(cls):
        # Configure maximum upload size (10GB) - Still relevant for local uploads
        MAX_UPLOAD_SIZE = 10 * 1024 * 1024 * 1024  # 10GB in bytes

        # Update the server's maximum client size
        if hasattr(PromptServer.instance, "app"):
            PromptServer.instance.app._client_max_size = MAX_UPLOAD_SIZE

        def get_s3_client():
            # Consider memoization or a shared client instance if performance is critical
            return boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION"),
            )

        # Updated validation for S3 path-based upload
        def validate_s3_path_upload_parts(model_path, checksum, filename, model_type):
            if not model_path:
                raise ValueError("No model_path part received")
            if not checksum:
                raise ValueError("No checksum part received")
            if not filename:
                raise ValueError("No filename part received")
            if not model_type:
                raise ValueError("No type part received")
            # Check if the model path actually exists
            if not os.path.isfile(model_path):
                # Return 404 specifically for this case
                raise FileNotFoundError(f"Model file not found at path: {model_path}")

        # Validation for local file upload (multipart)
        def validate_local_upload_parts(file_part, model_type, filename, file_data):
            if not file_part:
                raise ValueError("No file part received")
            if not model_type:
                raise ValueError("No type part received")
            if not filename:
                raise ValueError("No filename provided")
            if not file_data:
                raise ValueError("No file data received")

        def validate_model_directory(model_type):
            if model_type not in folder_paths.folder_names_and_paths:
                raise ValueError(f"Invalid model type: {model_type}")

            model_dirs = folder_paths.folder_names_and_paths[model_type][0]
            if not model_dirs:
                raise ValueError(f"No directory configured for model type: {model_type}")

            model_dir = model_dirs[0]
            logging.info(f"Using model directory: {model_dir}")

            # Create directory if it doesn't exist
            if not os.path.exists(model_dir):
                logging.info(f"Creating model directory: {model_dir}")
                os.makedirs(model_dir, exist_ok=True)

            return model_dir

        def write_file_data(filepath, file_data):
            logging.info("Starting to write file data...")
            total_size = len(file_data)
            logging.info(f"Writing {total_size / (1024 * 1024):.2f} MB of data")

            with open(filepath, "wb") as f:
                f.write(file_data)
                f.flush()
                os.fsync(f.fileno())

            # Verify file was written correctly
            actual_size = os.path.getsize(filepath)
            logging.info(f"File write complete. Expected size: {total_size}, Actual size: {actual_size}")

            if actual_size == 0:
                raise ValueError("File was created but contains no data")

            if actual_size != total_size:
                raise ValueError(f"File size mismatch. Expected: {total_size}, Got: {actual_size}")

            return total_size

        @PromptServer.instance.routes.post("/upload/s3-model")
        async def upload_s3_model(request):
            s3_client = None
            try:
                data = await request.post()
                model_path = data.get("model_path")
                checksum = data.get("checksum")
                filename = data.get("filename")
                model_type = data.get("type")

                logging.info(
                    f"Processing S3 path upload request: path={model_path}, checksum={checksum}, filename={filename}"
                )

                validate_s3_path_upload_parts(model_path, checksum, filename, model_type)

                s3_bucket = os.getenv("AWS_S3_MODEL_BUCKET")
                if not s3_bucket:
                    raise ValueError("AWS_S3_MODEL_BUCKET environment variable not set")

                s3_key_prefix = f"{checksum}/"
                target_s3_key = f"{s3_key_prefix}{filename}"

                s3_client = get_s3_client()

                # --- Check S3 before upload ---
                try:
                    list_response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=s3_key_prefix, MaxKeys=5)
                    objects_found = list_response.get("Contents", [])

                    print("objects_found", objects_found)
                    print("s3_key_prefix", s3_key_prefix)

                    if objects_found:
                        exact_match_found = False
                        found_key = ""
                        for obj in objects_found:
                            found_key = obj.get("Key", "")
                            if found_key == target_s3_key:
                                exact_match_found = True
                                break  # Found exact match, no need to check further

                        if exact_match_found:
                            # Scenario 1: Exact match already exists
                            logging.info(f"Exact match found in S3, skipping upload: {target_s3_key}")
                            return web.json_response(
                                {
                                    "status": "exists",
                                    "message": "File with this checksum and filename already exists in S3.",
                                    "name": filename,
                                    "type": model_type,
                                    "checksum": checksum,
                                    "s3_path": f"s3://{s3_bucket}/{target_s3_key}",
                                }
                            )
                        else:
                            # Scenario 2: Checksum exists, but filename differs
                            # Use the key of the first object found under the prefix as the expected name
                            expected_key = objects_found[0].get("Key", s3_key_prefix + "[unknown]")  # Fallback key
                            expected_filename = os.path.basename(expected_key)
                            error_msg = f"""File content (checksum {checksum}) exists in S3, but with a different name:
                            '{expected_filename}'. The requested filename was '{filename}'.
                            Please change the model name and try again."""
                            logging.warning(f"S3 Name Mismatch: {error_msg}")
                            return web.json_response(
                                {
                                    "status": "error",
                                    "error_type": "name_mismatch",
                                    "message": error_msg,
                                    "name": filename,
                                    "type": model_type,
                                    "checksum": checksum,
                                    "expected_name": expected_filename,
                                    "existing_s3_key": expected_key,
                                },
                                status=409,  # Conflict
                            )

                    # Scenario 3: Checksum does not exist, proceed with upload
                    logging.info(f"Checksum {checksum} not found in S3, proceeding with upload to {target_s3_key}")

                except ClientError as e:
                    logging.error(f"Error checking S3 bucket {s3_bucket} for prefix {s3_key_prefix}: {e}")
                    # Decide if this is fatal or if we should attempt upload anyway?
                    return web.Response(status=500, text=f"Error checking S3 before upload: {e}")
                # --- End S3 Check ---

                # --- Proceed with Upload (Only if Scenario 3) ---
                logging.info(f"Uploading to S3: {s3_bucket}/{target_s3_key} from local path: {model_path}")
                try:
                    with open(model_path, "rb") as f:
                        s3_client.upload_fileobj(f, s3_bucket, target_s3_key)
                    logging.info("S3 upload successful")

                    return web.json_response(
                        {
                            "status": "success",  # Explicitly mark successful uploads
                            "message": "File uploaded successfully to S3.",
                            "name": filename,
                            "type": model_type,
                            "checksum": checksum,
                            "s3_path": f"s3://{s3_bucket}/{target_s3_key}",
                        }
                    )
                except ClientError as e:
                    error_msg = f"AWS S3 upload error: {str(e)}"
                    logging.error(error_msg)
                    return web.Response(status=500, text=error_msg)
                except Exception as e:
                    error_msg = f"Error reading file or uploading to S3: {str(e)}"
                    logging.error(error_msg)
                    logging.error(traceback.format_exc())
                    return web.Response(status=500, text=error_msg)
                # --- End Upload ---

            except FileNotFoundError as e:
                error_msg = str(e)
                logging.error(f"File not found error during S3 upload processing: {error_msg}")
                return web.Response(status=404, text=error_msg)  # Use 404 for file not found
            except ValueError as e:
                error_msg = str(e)
                logging.error(f"ValueError during S3 path upload: {error_msg}")
                return web.Response(status=400, text=error_msg)
            except Exception as e:
                error_msg = str(e)
                logging.error(f"General error during S3 path upload: {error_msg}")
                logging.error(traceback.format_exc())
                return web.Response(status=500, text=f"Error processing S3 upload request: {error_msg}")

        @PromptServer.instance.routes.post("/upload/local-model")
        async def upload_local_model(request):
            try:
                # This route still handles direct file uploads via multipart
                request._client_max_size = MAX_UPLOAD_SIZE

                reader = await request.multipart()
                logging.info("Processing local model upload request...")

                file_part = None
                model_type = None
                filename = None
                file_data = None

                async for part in reader:
                    if part.name == "file":
                        file_part = part
                        filename = part.filename
                        file_data = await file_part.read()
                    elif part.name == "type":
                        model_type = await part.text()
                    else:
                        await part.read()

                # Use the original validation for local uploads
                validate_local_upload_parts(file_part, model_type, filename, file_data)

                logging.info(f"Processing local upload - Type: {model_type}, File: {filename}")

                model_dir = validate_model_directory(model_type)
                if not isinstance(model_dir, str) or not isinstance(filename, str):
                    raise ValueError("Invalid model directory or filename type")
                filepath = os.path.join(model_dir, filename)
                logging.info(f"Target filepath: {filepath}")

                try:
                    total_size = write_file_data(filepath, file_data)
                    logging.info(f"Model uploaded locally successfully to {filepath}")
                    return web.json_response(
                        {
                            "status": "success",
                            "name": filename,
                            "type": model_type,
                            "path": filepath,
                            "size": total_size,
                        }
                    )
                except Exception as e:
                    logging.error(f"Error while writing local file: {str(e)}")
                    logging.error(traceback.format_exc())
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                            logging.info(f"Cleaned up partial local file: {filepath}")
                        except Exception as cleanup_error:
                            logging.error(f"Error cleaning up partial local file: {str(cleanup_error)}")
                    raise

            except ValueError as e:
                error_msg = str(e)
                logging.error(f"ValueError during local upload: {error_msg}")
                if "File size exceeds maximum allowed size" in error_msg:
                    return web.Response(status=413, text="File too large: Maximum allowed size is 10GB")
                return web.Response(status=400, text=error_msg)
            except Exception as e:
                error_msg = str(e)
                logging.error(f"Error uploading local model: {error_msg}")
                logging.error(traceback.format_exc())
                return web.Response(status=500, text=f"Error uploading local model: {error_msg}")

        def setup_routes(cls):
            cls.upload_local_model()
            cls.upload_s3_model()
