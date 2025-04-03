import imghdr
import json
import logging
import os
import sys
import traceback

import aiohttp
import folder_paths
from aiohttp import web
from signature_flows.manifests import WorkflowManifest
from signature_flows.workflow import Workflow

from .. import BASE_COMFY_DIR

current_dir = os.getcwd()
sys.path.append(BASE_COMFY_DIR)
from server import PromptServer  # type: ignore # noqa: E402

sys.path.append(current_dir)


class SignatureFlowService:
    @classmethod
    def setup_routes(cls):
        @PromptServer.instance.routes.post("/flow/create_manifest")
        async def create_manifest(request):
            try:
                json_data = await request.json()
                workflow_data = json_data.get("workflow")
                if not workflow_data:
                    return web.json_response(text="No workflow data provided", status=400)
                if isinstance(workflow_data, dict):
                    workflow_data = json.dumps(workflow_data)
                wf = Workflow(workflow_data)
                manifest = WorkflowManifest(workflow=wf, comfy_dir=BASE_COMFY_DIR)
                return web.json_response(manifest.get_json(), status=200)
            except Exception as e:
                error_msg = f"Error creating manifest: {str(e)}\n{traceback.format_exc()}"
                logging.error(error_msg)
                return web.json_response(text=error_msg, status=500)

        @PromptServer.instance.routes.post("/flow/workflow_data")
        async def workflow_data(request):
            try:
                json_data = await request.json()
                workflow_data = json_data.get("workflow")
                if not workflow_data:
                    return web.json_response(text="No workflow data provided", status=400)

                if isinstance(workflow_data, dict):
                    workflow_data = json.dumps(workflow_data)

                wf = Workflow(workflow_data)
                io = {
                    "workflow_api": wf.get_dict(),
                    "inputs": wf.get_inputs(),
                    "outputs": wf.get_outputs(),
                }
                return web.json_response(io, status=200)
            except Exception as e:
                error_msg = f"Error creating manifest: {str(e)}\n{traceback.format_exc()}"
                logging.error(error_msg)
                return web.json_response(text=error_msg, status=500)

        # Configure maximum upload size (10GB)
        MAX_UPLOAD_SIZE = 10 * 1024 * 1024 * 1024  # 10GB in bytes

        # Update the server's maximum client size
        if hasattr(PromptServer.instance, "app"):
            PromptServer.instance.app._client_max_size = MAX_UPLOAD_SIZE

        def validate_upload_parts(file_part, model_type, filename, file_data):
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

        @PromptServer.instance.routes.post("/upload/model")
        async def upload_model(request):
            try:
                # Configure request to handle large files
                request._client_max_size = MAX_UPLOAD_SIZE

                reader = await request.multipart()
                logging.info("Processing upload request...")

                # Log request details
                logging.info("Request details:")
                logging.info(f"Content-Type: {request.content_type}")
                logging.info(f"Content-Length: {request.content_length}")

                file_part = None
                model_type = None
                filename = None
                file_data = None

                # Process all parts
                async for part in reader:
                    logging.info(f"Processing part: {part.name}")

                    if part.name == "file":
                        file_part = part
                        filename = part.filename
                        file_data = await file_part.read()
                    elif part.name == "type":
                        model_type = await part.text()
                        logging.info(f"Found type part: {model_type}")
                    else:
                        logging.info(f"Skipping part: {part.name}")
                        await part.read()  # Read and discard other parts

                # Validate required parts
                validate_upload_parts(file_part, model_type, filename, file_data)

                logging.info(f"Processing upload - Type: {model_type}, File: {filename}")

                # Validate model type and get directory
                model_dir = validate_model_directory(model_type)
                if not isinstance(model_dir, str) or not isinstance(filename, str):
                    raise ValueError("Invalid model directory or filename type")
                filepath = os.path.join(model_dir, filename)
                logging.info(f"Target filepath: {filepath}")

                # Save the file
                try:
                    total_size = write_file_data(filepath, file_data)
                    logging.info(f"Model uploaded successfully to {filepath}")
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
                    logging.error(f"Error while writing file: {str(e)}")
                    logging.error(traceback.format_exc())
                    # Clean up partial file if it exists
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                            logging.info(f"Cleaned up partial file: {filepath}")
                        except Exception as cleanup_error:
                            logging.error(f"Error cleaning up partial file: {str(cleanup_error)}")
                    raise

            except ValueError as e:
                error_msg = str(e)
                logging.error(f"ValueError during upload: {error_msg}")
                if "File size exceeds maximum allowed size" in error_msg:
                    return web.Response(status=413, text="File too large: Maximum allowed size is 10GB")
                return web.Response(status=400, text=error_msg)
            except Exception as e:
                error_msg = str(e)
                logging.error(f"Error uploading model: {error_msg}")
                logging.error(traceback.format_exc())
                return web.Response(status=500, text=f"Error uploading model: {error_msg}")

        @PromptServer.instance.routes.post("/flow/submit_workflow")
        async def submit_workflow(request: web.BaseRequest):
            try:
                jenkins_url = os.getenv("JENKINS_URL")
                jenkins_auth = os.getenv("JENKINS_AUTH")

                if not jenkins_url or not jenkins_auth:
                    raise ValueError("JENKINS_URL and JENKINS_AUTH environment variables must be set")

                jenkins_url = jenkins_url.rstrip("/") + "/job/Submit%20Workflow/buildWithParameters"
                auth = f"Basic {jenkins_auth}"

                form_data = await request.multipart()
                new_form_data = aiohttp.FormData()

                logging.info("Starting to process form data")
                async for part in form_data:
                    if not isinstance(part, aiohttp.BodyPartReader) or part.name is None:
                        continue

                    field_name = part.name
                    logging.info(f"Processing field: {field_name}")

                    if part.filename:
                        content = await part.read()
                        new_form_data.add_field(field_name, content, filename=part.filename)
                    else:
                        content = await part.text()
                        if field_name == "coverImageUrl":
                            logging.info(f"Processing coverImageUrl: {content}")
                            try:
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(
                                        content, timeout=aiohttp.ClientTimeout(total=10)
                                    ) as response:
                                        logging.info(f"Cover image fetch status: {response.status}")
                                        if response.status == 200:
                                            image_data = await response.read()
                                            logging.info(
                                                f"Successfully fetched image data, size: {len(image_data)} bytes"
                                            )
                                            # Extract filename from URL
                                            image_name = content.split("/")[-1]
                                            # Add logging for image details
                                            image_format = imghdr.what(None, h=image_data)
                                            logging.info(f"Image format: {image_format}")
                                            logging.info(f"Image name: {image_name}")
                                            new_form_data.add_field(
                                                name="coverImage",
                                                value=image_data,
                                                content_type=f"image/{image_format}",
                                                filename=f"{image_name}.{image_format}",  # Add filename to form data
                                            )
                                            logging.info("Added coverImage to form data")
                                        else:
                                            logging.warning("Failed to fetch cover image")
                                            raise Exception(f"Failed to fetch image: {response.status}")
                            except Exception as e:
                                logging.error(f"Error processing coverImageUrl: {str(e)}")
                                raise
                        else:
                            new_form_data.add_field(field_name, content)

                # Log the final form data fields
                logging.info("Final form data fields:")

                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": auth}
                    async with session.post(jenkins_url, data=new_form_data, headers=headers) as resp:
                        if resp.status != 201:
                            logging.error(
                                "Workflow submission failed with status: %d",
                                resp.status,
                            )
                            return web.json_response(text="Workflow submission failed", status=502)
                        return web.json_response(text="Workflow submitted successfully", status=200)

            except Exception as e:
                base_error_msg = "Error while submitting workflow"
                error_msg = f"{base_error_msg}: {str(e)}\n{traceback.format_exc()}"
                logging.error(error_msg)
                return web.json_response(text=base_error_msg, status=500)

    logging.info("SignatureFlowService Started")
