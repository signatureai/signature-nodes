import logging
import os
import sys
import traceback

from aiohttp import web

from ..shared import BASE_COMFY_DIR

sys.path.append(BASE_COMFY_DIR)
import folder_paths  # type: ignore # noqa: E402
from server import PromptServer  # type: ignore # noqa: E402

current_dir = os.getcwd()
sys.path.append(current_dir)


class SignatureModelService:
    @classmethod
    def setup_routes(cls):
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
