import imghdr
import json
import logging
import os
import sys
import traceback

import aiohttp
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
