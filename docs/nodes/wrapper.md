# Wrapper Nodes

## Wrapper

A wrapper class for handling workflow execution and communication with a remote server.

This class provides functionality to execute workflows, process inputs/outputs, and handle
communication with a remote server. It supports uploading files, running workflow jobs, and
processing various types of data including images, masks, and primitive types.

??? note "Source code in wrapper.py"

    ```python
    class Wrapper:
        """A wrapper class for handling workflow execution and communication with a remote server.

        This class provides functionality to execute workflows, process inputs/outputs, and handle
        communication with a remote server. It supports uploading files, running workflow jobs, and
        processing various types of data including images, masks, and primitive types.

        Args:
            data (str, optional): JSON string containing workflow configuration and execution parameters.
                Default is an empty string.

        Returns:
            tuple: A tuple of length 20 containing processed outputs from the workflow execution.
                Each element can be of any type (images, numbers, strings, etc.) or None.

        Raises:
            Exception:
                - If communication with the server fails after multiple retries
                - If the workflow execution encounters an error
                - If required parameters (base_url, workflow_api, token) are missing or invalid

        Notes:
            The class provides several key features:
            - Uses a placeholder server for local execution
            - Supports various input types including IMAGE, MASK, INT, FLOAT, BOOLEAN, and STRING
            - Handles tensor image conversions and S3 uploads
            - Manages memory by cleaning up models and cache after execution
            - Uses progress bars to track workflow execution
            - Implements retry logic for handling communication issues
        """

        def __init__(self):
            self.total_steps = 0
            self.remaining_ids = []
            self.server = None
            self.executor = None

        def get_workflow(self, base_url: str, workflow_id: str, token: str) -> dict:
            url = f"{base_url}/workflows/{workflow_id}"
            headers = {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Authorization": "Bearer " + token,
            }
            output = {}
            with httpx.Client() as client:
                try:
                    response = client.get(url, headers=headers, timeout=3)
                    if response.status_code == 200:
                        buffer = response.content
                        output = json.loads(buffer)
                except Exception as e:
                    console.log(e)
            return output

        def process_outputs(self, job_outputs, node_outputs):

            def process_data(node_output: dict, job_output: dict):

                node_type = node_output.get("type")
                value = job_output.get("value")
                if value is None or not isinstance(node_type, str):
                    return []
                if node_type in ("IMAGE", "MASK"):
                    if not isinstance(value, str):
                        return None
                    image_path = os.path.join(BASE_COMFY_DIR, "output", value)
                    output_image = TensorImage.from_local(image_path)
                    return output_image.get_BWHC()
                if node_type == "INT":
                    return int(value)
                if node_type == "FLOAT":
                    return float(value)
                if node_type == "BOOLEAN":
                    return bool(value)
                return str(value)

            outputs = []
            for node_output in node_outputs:
                for job_output in job_outputs:
                    if not isinstance(job_output, dict) or not isinstance(node_output, dict):
                        continue
                    node_name = node_output.get("title") or []
                    job_name = job_output.get("title") or []
                    if isinstance(node_name, str):
                        node_name = [node_name]
                    if isinstance(job_name, str):
                        job_name = [job_name]
                    # console.log(f"Node name: {node_name}, Job name: {job_name}")
                    for node_name_part in node_name:
                        for job_name_part in job_name:
                            if node_name_part != job_name_part:
                                continue
                            data = process_data(node_output, job_output)
                            if data is None:
                                continue
                            outputs.append(data)
                            break
                    # console.log(f"Added {node_name} {node_type}")
            # console.log(f"=====================>>> Node outputs: {len(outputs)}")
            return tuple(outputs)

        @classmethod
        def INPUT_TYPES(cls):  # type: ignore
            inputs = {
                "required": {
                    "data": ("STRING", {"default": ""}),
                },
                "optional": {},
            }

            return inputs

        RETURN_TYPES = (any_type,) * 20
        FUNCTION = "execute"
        CATEGORY = LABS_CAT

        def execute(self, **kwargs):

            data = kwargs.get("data")
            # console.log(f"kwargs: {kwargs}")

            fallback = (None,) * 20
            if data is None:
                return fallback
            json_data = json.loads(data)
            if not isinstance(json_data, dict):
                return fallback
            base_url = json_data.get("origin") or None
            workflow_api = json_data.get("workflow_api") or None
            token = json_data.get("token") or None
            inference_host = json_data.get("inference_host") or None
            widget_inputs = json_data.get("widget_inputs") or []
            # console.log(f"Widget inputs: {widget_inputs}")

            if inference_host is None or inference_host == "":
                inference_host = base_url
            # console.log(f"Origin: {base_url}, Inference host: {inference_host}")
            if not isinstance(base_url, str):
                return fallback
            if not isinstance(workflow_api, dict):
                return fallback
            if not isinstance(token, str):
                return fallback

            workflow = Workflow(workflow_api)
            node_inputs = workflow.get_inputs()
            # console.log(f"Node inputs: {node_inputs}")
            workflow_outputs = workflow.get_outputs()
            output_ids = workflow_outputs.keys()
            node_outputs = workflow_outputs.values()
            # console.log(f"Node outputs: {node_outputs}")

            for key, value in node_inputs.items():
                if not isinstance(value, dict):
                    continue
                node_title = value.get("title")
                node_type = value.get("type")
                if not isinstance(node_type, str) or not isinstance(node_title, str):
                    continue
                comfy_value = kwargs.get(node_title)
                if comfy_value is None:
                    for widget_input in widget_inputs:
                        if widget_input.get("title") == node_title:
                            widget_value = widget_input.get("value")
                            if widget_value is None:
                                continue
                            comfy_value = widget_input.get("value")
                            break
                if comfy_value is None:
                    continue
                if node_type in ("IMAGE", "MASK"):
                    if isinstance(comfy_value, torch.Tensor):
                        tensor_image = TensorImage.from_BWHC(comfy_value).get_base64()
                        value.update({"value": tensor_image})
                        node_inputs[key] = value
                else:
                    value.update({"value": comfy_value})
                    node_inputs[key] = value

            workflow.set_inputs(node_inputs)
            workflow_api = workflow.data

            if not isinstance(workflow_api, dict):
                return fallback

            total_nodes = list(workflow_api.keys())
            self.total_steps = len(total_nodes)
            self.remaining_ids = total_nodes
            pbar = ProgressBar(self.total_steps)  # type: ignore

            def report_handler(event, data, _):
                if event == "execution_start":
                    prompt_id = data.get("prompt_id")
                    console.log(f"Wrapper Execution started, prompt {prompt_id}")
                elif event == "execution_cached":
                    cached_nodes_ids = data.get("nodes", []) or []
                    self.remaining_ids = list(set(self.remaining_ids) - set(cached_nodes_ids))
                elif event == "executing":
                    node_id = data.get("node")
                    self.remaining_ids = list(set(self.remaining_ids) - {node_id})
                elif event == "execution_error":
                    console.log(f"Execution error: {data}")
                    raise Exception(data.get("error"))
                elif event == "execution_interrupted":
                    raise Exception("Execution was interrupted")
                elif event == "executed":
                    prompt_id = data.get("prompt_id")
                    self.remaining_ids = []
                    console.log(f"Wrapper Execution finished, prompt {prompt_id}")
                pbar.update_absolute(self.total_steps - len(self.remaining_ids), self.total_steps)
                percentage = 100 * round((self.total_steps - len(self.remaining_ids)) / self.total_steps, 2)
                console.log(f"Wrapper Execution: {percentage}%")

            self.server = PlaceholderServer(report_handler)
            self.executor = execution.PromptExecutor(self.server)  # type: ignore
            self.executor.execute(workflow_api, uuid.uuid4(), {"client_id": self.server.client_id}, output_ids)
            self.executor.reset()
            gc.collect()
            comfy.model_management.unload_all_models()
            comfy.model_management.cleanup_models()
            comfy.model_management.soft_empty_cache()

            if self.executor.success:
                console.log("Success wrapper inference")
            else:
                console.log("Failed wrapper inference")
                final_status = self.executor.status_messages[-1]
                console.log(f"Final status: {final_status}")
                if isinstance(final_status, dict):
                    final_error = final_status.get("execution_error") or None
                    if final_error is not None:
                        raise Exception(final_error)
            outputs = self.executor.history_result["outputs"].values()
            job_outputs = []
            for job_output in outputs:
                for key, value in job_output.items():
                    if key == "signature_output":
                        job_outputs.extend(value)

            return self.process_outputs(job_outputs, node_outputs)

    ```
