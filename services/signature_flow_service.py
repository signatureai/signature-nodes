from .. import SIGNATURE_FLOWS_AVAILABLE

if SIGNATURE_FLOWS_AVAILABLE:
    import json
    import logging
    import os
    import sys
    import traceback

    from aiohttp import web
    from signature_flows.manifests import WorkflowManifest
    from signature_flows.workflow import Workflow

    from .. import BASE_COMFY_DIR

    current_dir = os.getcwd()
    sys.path.append(BASE_COMFY_DIR)
    from server import PromptServer  # type: ignore

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
                        return web.json_response({"error": "No workflow data provided"}, status=400)
                    if isinstance(workflow_data, dict):
                        workflow_data = json.dumps(workflow_data)
                    wf = Workflow(workflow_data)
                    manifest = WorkflowManifest(workflow=wf, comfy_dir=BASE_COMFY_DIR)
                    output = manifest.get_json()
                    return web.json_response(output)

                except Exception as e:
                    error_msg = f"Error creating manifest: {str(e)}\n{traceback.format_exc()}"
                    logging.error(error_msg)
                    return web.json_response({"error": error_msg}, status=500)

            @PromptServer.instance.routes.post("/flow/workflow_data")
            async def workflow_data(request):
                try:
                    json_data = await request.json()
                    workflow_data = json_data.get("workflow")
                    if not workflow_data:
                        return web.json_response({"error": "No workflow data provided"}, status=400)

                    if isinstance(workflow_data, dict):
                        workflow_data = json.dumps(workflow_data)

                    wf = Workflow(workflow_data)
                    io = {
                        "workflow_api": wf.get_dict(),
                        "inputs": wf.get_inputs(),
                        "outputs": wf.get_outputs(),
                    }
                    return web.json_response(io)

                except Exception as e:
                    error_msg = f"Error creating manifest: {str(e)}\n{traceback.format_exc()}"
                    logging.error(error_msg)
                    return web.json_response({"error": error_msg}, status=500)

            logging.info("SignatureFlowService Started")
