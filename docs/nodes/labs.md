# Labs Nodes

## Wrapper

A wrapper class for handling workflow execution and communication with a remote server.

This class provides functionality to execute workflows, process inputs/outputs, and handle
communication with a remote server. It supports uploading files, running workflow jobs, and
processing various types of data including images, masks, and primitive types.

??? note "Source code"

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

## Switch

Switches between two input values based on a boolean condition.

A logic gate that selects between two inputs of any type based on a boolean condition. When the
condition is True, it returns the 'true' value; otherwise, it returns the 'false' value. This node
is useful for creating conditional workflows and dynamic value selection.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | condition | `BOOLEAN` | True |  |
| required | on_true | `any_type` |  |  |
| required | on_false | `any_type` |  |  |

??? note "Source code"

    ```python
    class Switch:
        """Switches between two input values based on a boolean condition.

        A logic gate that selects between two inputs of any type based on a boolean condition. When the
        condition is True, it returns the 'true' value; otherwise, it returns the 'false' value. This node
        is useful for creating conditional workflows and dynamic value selection.

        Args:
            condition (bool): The boolean condition that determines which value to return.
                Defaults to False if not provided.
            on_true (Any): The value to return when the condition is True. Can be of any type.
            on_false (Any): The value to return when the condition is False. Can be of any type.

        Returns:
            tuple[Any]: A single-element tuple containing either the 'true' or 'false' value based on
                the condition.

        Notes:
            - The node accepts inputs of any type, making it versatile for different data types
            - Both 'on_true' and 'on_false' values must be provided
            - The condition is automatically cast to boolean, with None being treated as False
        """

        @classmethod
        def INPUT_TYPES(cls):  # type: ignore
            return {
                "required": {
                    "condition": ("BOOLEAN", {"default": True}),
                    "on_true": (any_type,),
                    "on_false": (any_type,),
                }
            }

        RETURN_TYPES = (any_type,)
        RETURN_NAMES = ("output",)
        FUNCTION = "execute"
        CATEGORY = LOGIC_CAT

        def check_lazy_status(self, condition, on_true=None, on_false=None):
            if condition and on_true is None:
                on_true = ["on_true"]
                if isinstance(on_true, ExecutionBlocker):
                    on_true = on_true.message  # type: ignore
                return on_true
            if not condition and on_false is None:
                on_false = ["on_false"]
                if isinstance(on_false, ExecutionBlocker):
                    on_false = on_false.message  # type: ignore
                return on_false
            return None

        def execute(self, **kwargs):
            return (kwargs["on_true"] if kwargs["condition"] else kwargs["on_false"],)


    ```

## Blocker

Controls flow execution based on a boolean condition.

A utility node that blocks or allows execution flow based on a boolean flag. When the continue
flag is False, it blocks execution by returning an ExecutionBlocker. When True, it passes through
the input value unchanged.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | continue | `BOOLEAN` | False |  |
| required | in | `any_type` | None |  |

??? note "Source code"

    ```python
    class Blocker:
        """Controls flow execution based on a boolean condition.

        A utility node that blocks or allows execution flow based on a boolean flag. When the continue
        flag is False, it blocks execution by returning an ExecutionBlocker. When True, it passes through
        the input value unchanged.

        Args:
            continue (bool): Flag to control execution flow. When False, blocks execution.
            in (Any): The input value to pass through when execution is allowed.

        Returns:
            tuple[Any]: A single-element tuple containing either:
                - The input value if continue is True
                - An ExecutionBlocker if continue is False

        Notes:
            - Useful for conditional workflow execution
            - Can be used to create branches in execution flow
            - The ExecutionBlocker prevents downstream nodes from executing
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "continue": ("BOOLEAN", {"default": False}),
                    "in": (any_type, {"default": None}),
                },
            }

        RETURN_TYPES = (any_type,)
        RETURN_NAMES = ("out",)
        CATEGORY = LABS_CAT
        FUNCTION = "execute"

        def execute(self, **kwargs):
            return (kwargs["in"] if kwargs["continue"] else ExecutionBlocker(None),)


    ```

## Compare

Compares two input values based on a specified comparison operation.

A logic gate that evaluates a comparison between two inputs of any type. The comparison is determined
by the specified operation, which can include equality, inequality, and relational comparisons. This
node is useful for implementing conditional logic based on the relationship between two values.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | a | `any_type` |  |  |
| required | b | `any_type` |  |  |
| required | comparison | `compare_functions` | a == b |  |

### Returns

| Name | Type |
|------|------|
| boolean | `BOOLEAN` |


??? note "Source code"

    ```python
    class Compare:
        """Compares two input values based on a specified comparison operation.

        A logic gate that evaluates a comparison between two inputs of any type. The comparison is determined
        by the specified operation, which can include equality, inequality, and relational comparisons. This
        node is useful for implementing conditional logic based on the relationship between two values.

        Args:
            a (Any): The first value to compare. Can be of any type.
            b (Any): The second value to compare. Can be of any type.
            comparison (str): The comparison operation to perform. Defaults to "a == b".
                Available options include:
                - "a == b": Checks if a is equal to b.
                - "a != b": Checks if a is not equal to b.
                - "a < b": Checks if a is less than b.
                - "a > b": Checks if a is greater than b.
                - "a <= b": Checks if a is less than or equal to b.
                - "a >= b": Checks if a is greater than or equal to b.

        Returns:
            tuple[bool]: A single-element tuple containing the result of the comparison as a boolean value.

        Notes:
            - The node accepts inputs of any type, making it versatile for different data types.
            - If the inputs are tensors, lists, or tuples,
              the comparison will be evaluated based on their shapes or lengths.
            - The output will be cast to a boolean value.
        """

        COMPARE_FUNCTIONS = {
            "a == b": lambda a, b: a == b,
            "a != b": lambda a, b: a != b,
            "a < b": lambda a, b: a < b,
            "a > b": lambda a, b: a > b,
            "a <= b": lambda a, b: a <= b,
            "a >= b": lambda a, b: a >= b,
        }

        @classmethod
        def INPUT_TYPES(cls):  # type: ignore
            compare_functions = list(cls.COMPARE_FUNCTIONS.keys())
            return {
                "required": {
                    "a": (any_type,),
                    "b": (any_type,),
                    "comparison": (compare_functions, {"default": "a == b"}),
                }
            }

        RETURN_TYPES = ("BOOLEAN",)
        RETURN_NAMES = ("result",)
        FUNCTION = "execute"
        CATEGORY = LOGIC_CAT

        def execute(self, **kwargs):
            input_a = kwargs.get("a")
            input_b = kwargs.get("b")
            comparison = kwargs.get("comparison") or "a == b"

            try:
                output = self.COMPARE_FUNCTIONS[comparison](input_a, input_b)
            except Exception as e:
                if isinstance(input_a, torch.Tensor) and isinstance(input_b, torch.Tensor):
                    output = self.COMPARE_FUNCTIONS[comparison](input_a.shape, input_b.shape)
                elif isinstance(input_a, (list, tuple)) and isinstance(input_b, (list, tuple)):
                    output = self.COMPARE_FUNCTIONS[comparison](len(input_a), len(input_b))
                else:
                    raise e

            if isinstance(output, torch.Tensor):
                output = output.all().item()
            elif isinstance(output, (list, tuple)):
                output = all(output)

            return (bool(output),)


    ```

## LoopStart

Initiates a loop with optional initial values for each iteration.

A control node that starts a loop, allowing for a specified number of iterations. It can accept
optional initial values for each iteration, which can be used within the loop. This node is useful
for creating iterative workflows where the same set of operations is performed multiple times.

??? note "Source code"

    ```python
    class LoopStart:
        """Initiates a loop with optional initial values for each iteration.

        A control node that starts a loop, allowing for a specified number of iterations. It can accept
        optional initial values for each iteration, which can be used within the loop. This node is useful
        for creating iterative workflows where the same set of operations is performed multiple times.

        Args:
            init_value (Any): The initial value for the first iteration. Can be of any type.

        Returns:
            tuple[tuple]: A tuple containing a flow control signal and the initial values for each iteration.

        Notes:
            - The number of initial values can be adjusted by changing the MAX_FLOW_NUM constant.
            - Each initial value can be of any type, providing flexibility for different workflows.
        """

        @classmethod
        def INPUT_TYPES(cls):
            inputs = {
                "optional": {},
            }
            for i in range(MAX_FLOW_NUM):
                inputs["optional"][f"init_value_{i}"] = (any_type,)
            return inputs

        RETURN_TYPES = ByPassTypeTuple(tuple(["FLOW_CONTROL"] + [any_type] * MAX_FLOW_NUM))
        RETURN_NAMES = ByPassTypeTuple(tuple(["flow"] + [f"value_{i}" for i in range(MAX_FLOW_NUM)]))
        FUNCTION = "execute"

        CATEGORY = LABS_CAT + "/Loops"

        def execute(self, **kwargs):
            values = []
            for i in range(MAX_FLOW_NUM):
                values.append(kwargs.get(f"init_value_{i}", None))
            return tuple(["stub"] + values)


    ```

## LoopEnd

Ends a loop and returns the final values after the loop execution.

A control node that signifies the end of a loop initiated by a `LoopStart` node. It processes the
flow control signal and can return the final values from the loop iterations. This node is useful
for managing the completion of iterative workflows and retrieving results after looping.

??? note "Source code"

    ```python
    class LoopEnd:
        """Ends a loop and returns the final values after the loop execution.

        A control node that signifies the end of a loop initiated by a `LoopStart` node. It processes the
        flow control signal and can return the final values from the loop iterations. This node is useful
        for managing the completion of iterative workflows and retrieving results after looping.

        Args:
            flow (FLOW_CONTROL): The flow control signal indicating the current state of the loop.
            end_loop (bool): A boolean flag that indicates whether to end the loop. If True, the loop will terminate.
            dynprompt (DYNPROMPT, optional): Dynamic prompt information for the node.
            unique_id (UNIQUE_ID, optional): A unique identifier for the loop instance.

        Returns:
            tuple: A tuple containing the final values from the loop iterations.

        Notes:
            - The loop can be terminated based on the `end_loop` flag,
              allowing for flexible control over the iteration process.
            - The number of returned values corresponds to the number of initial values provided in the `LoopStart`.
        """

        def __init__(self):
            pass

        @classmethod
        def INPUT_TYPES(cls):
            inputs = {
                "required": {
                    "flow": ("FLOW_CONTROL", {"rawLink": True}),
                    "end_loop": ("BOOLEAN", {}),
                },
                "optional": {},
                "hidden": {
                    "dynprompt": "DYNPROMPT",
                    "unique_id": "UNIQUE_ID",
                },
            }
            for i in range(MAX_FLOW_NUM):
                inputs["optional"][f"init_value_{i}"] = (any_type,)
            return inputs

        RETURN_TYPES = ByPassTypeTuple(tuple([any_type] * MAX_FLOW_NUM))
        RETURN_NAMES = ByPassTypeTuple(tuple(f"value_{i}" for i in range(MAX_FLOW_NUM)))
        FUNCTION = "execute"

        CATEGORY = LABS_CAT + "/Loops"

        def explore_dependencies(self, node_id, dynprompt, upstream):
            node_info = dynprompt.get_node(node_id)
            if "inputs" not in node_info:
                return
            for _, v in node_info["inputs"].items():
                if is_link(v):
                    parent_id = v[0]
                    if parent_id not in upstream:
                        upstream[parent_id] = []
                        self.explore_dependencies(parent_id, dynprompt, upstream)
                    upstream[parent_id].append(node_id)

        def collect_contained(self, node_id, upstream, contained):
            if node_id not in upstream:
                return
            for child_id in upstream[node_id]:
                if child_id not in contained:
                    contained[child_id] = True
                    self.collect_contained(child_id, upstream, contained)

        def execute(self, flow, end_loop, dynprompt=None, unique_id=None, **kwargs):
            if end_loop:
                # We're done with the loop
                values = []
                for i in range(MAX_FLOW_NUM):
                    values.append(kwargs.get(f"init_value_{i}", None))
                return tuple(values)

            # We want to loop
            if dynprompt is not None:
                _ = dynprompt.get_node(unique_id)
            upstream = {}
            # Get the list of all nodes between the open and close nodes
            self.explore_dependencies(unique_id, dynprompt, upstream)

            contained = {}
            open_node = flow[0]
            self.collect_contained(open_node, upstream, contained)
            contained[unique_id] = True
            contained[open_node] = True

            graph = GraphBuilder()
            for node_id in contained:
                if dynprompt is not None:
                    original_node = dynprompt.get_node(node_id)
                    node = graph.node(original_node["class_type"], "Recurse" if node_id == unique_id else node_id)
                    node.set_override_display_id(node_id)
            for node_id in contained:
                if dynprompt is not None:
                    original_node = dynprompt.get_node(node_id)
                    node = graph.lookup_node("Recurse" if node_id == unique_id else node_id)
                    for k, v in original_node["inputs"].items():
                        if is_link(v) and v[0] in contained:
                            parent = graph.lookup_node(v[0])
                            node.set_input(k, parent.out(v[1]))
                        else:
                            node.set_input(k, v)

            new_open = graph.lookup_node(open_node)
            for i in range(MAX_FLOW_NUM):
                key = f"init_value_{i}"
                new_open.set_input(key, kwargs.get(key, None))
            my_clone = graph.lookup_node("Recurse")
            result = map(lambda x: my_clone.out(x), range(MAX_FLOW_NUM))
            return {
                "result": tuple(result),
                "expand": graph.finalize(),
            }
    ```

## ApplyLoraStack

Applies multiple LoRA models sequentially to a base model and CLIP in ComfyUI.

This node takes a base model, CLIP, and a stack of LoRA models as input. It applies each LoRA
in the stack sequentially using specified weights for both model and CLIP components.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | model | `MODEL` |  |  |
| required | clip | `CLIP` |  |  |
| required | lora_stack | `LORA_STACK` |  |  |

### Returns

| Name | Type |
|------|------|
| model | `MODEL` |
| clip | `CLIP` |


??? note "Source code"

    ```python
    class ApplyLoraStack:
        """Applies multiple LoRA models sequentially to a base model and CLIP in ComfyUI.

        This node takes a base model, CLIP, and a stack of LoRA models as input. It applies each LoRA
        in the stack sequentially using specified weights for both model and CLIP components.

        Args:
            model (MODEL): The base Stable Diffusion model to modify
            clip (CLIP): The CLIP model to modify
            lora_stack (LORA_STACK): A list of tuples containing (lora_name, model_weight, clip_weight)

        Returns:
            tuple:
                - MODEL: The modified Stable Diffusion model with all LoRAs applied
                - CLIP: The modified CLIP model with all LoRAs applied

        Notes:
            - LoRAs are applied in sequence, with each modification building on previous changes
            - If lora_stack is None, returns the original model and CLIP unchanged
            - Uses ComfyUI's built-in LoRA loading and application mechanisms
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "model": ("MODEL",),
                    "clip": ("CLIP",),
                    "lora_stack": ("LORA_STACK",),
                }
            }

        RETURN_TYPES = (
            "MODEL",
            "CLIP",
        )
        RETURN_NAMES = (
            "MODEL",
            "CLIP",
        )
        FUNCTION = "execute"
        CATEGORY = LORA_CAT

        def execute(
            self,
            **kwargs,
        ):
            model = kwargs.get("model")
            clip = kwargs.get("clip")
            lora_stack = kwargs.get("lora_stack")
            loras = []
            if lora_stack is None:
                return (
                    model,
                    clip,
                )

            model_lora = model
            clip_lora = clip
            loras.extend(lora_stack)

            for lora in loras:
                lora_name, strength_model, strength_clip = lora

                lora_path = folder_paths.get_full_path("loras", lora_name)
                lora = utils.load_torch_file(lora_path, safe_load=True)

                model_lora, clip_lora = sd.load_lora_for_models(model_lora, clip_lora, lora, strength_model, strength_clip)

            return (
                model_lora,
                clip_lora,
            )


    ```

## LoraStacker

Manages multiple LoRA models with configurable weights and modes.

This node provides an interface for stacking multiple LoRA models with independent
weight controls and two operating modes for simple or advanced weight management.

### Returns

| Name | Type |
|------|------|
| lora_stack | `LORA_STACK` |


??? note "Source code"

    ```python
    class LoraStacker:
        """Manages multiple LoRA models with configurable weights and modes.

        This node provides an interface for stacking multiple LoRA models with independent
        weight controls and two operating modes for simple or advanced weight management.

        Args:
            num_slots (str): Number of LoRA slots to enable (1-10)
            mode (str): Weight control mode:
                - "Simple": Single weight per LoRA
                - "Advanced": Separate model and CLIP weights
            switch_1..10 (str): "On"/"Off" toggle for each LoRA slot
            lora_name_1..10 (str): Name of LoRA model for each slot
            weight_1..10 (float): Weight value for simple mode (-10.0 to 10.0)
            model_weight_1..10 (float): Model weight for advanced mode (-10.0 to 10.0)
            clip_weight_1..10 (float): CLIP weight for advanced mode (-10.0 to 10.0)
            lora_stack (LORA_STACK, optional): Existing stack to extend

        Returns:
            tuple[LORA_STACK]: Single-element tuple containing list of configured LoRAs

        Notes:
            - Each slot can be independently enabled/disabled
            - Simple mode uses same weight for model and CLIP
            - Advanced mode allows separate model and CLIP weights
            - Weights can be negative for inverse effects
            - Can extend existing LORA_STACK
            - Disabled or empty slots are skipped
        """

        @classmethod
        def INPUT_TYPES(cls):
            loras = ["None"] + folder_paths.get_filename_list("loras")

            inputs = {
                "required": {
                    "num_slots": ([str(i) for i in range(1, 11)], {"default": "1"}),
                    "mode": (["Simple", "Advanced"],),
                },
                "optional": {"lora_stack": ("LORA_STACK",)},
            }

            for i in range(1, 11):
                inputs["optional"].update(
                    {
                        f"switch_{i}": (["On", "Off"],),
                        f"lora_name_{i}": (loras,),
                        f"weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                        f"model_weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                        f"clip_weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    }
                )

            return inputs

        RETURN_TYPES = ("LORA_STACK",)
        RETURN_NAMES = ("lora_stack",)
        FUNCTION = "execute"
        CATEGORY = LABS_CAT
        CLASS_ID = "lora_stacker"

        def execute(self, **kwargs):
            num_slots = int(kwargs.get("num_slots", 3))
            mode = kwargs.get("mode", "Simple")
            lora_stack = kwargs.get("lora_stack")

            lora_list: list = []
            if lora_stack is not None:
                lora_list.extend([l for l in lora_stack if l[0] is not None and l[0] != ""])

            for i in range(1, num_slots + 1):
                switch = kwargs.get(f"switch_{i}")
                lora_name = kwargs.get(f"lora_name_{i}") or "None"

                if lora_name is not None and lora_name != "None" and switch == "On":
                    if mode == "Simple":
                        weight = float(kwargs.get(f"weight_{i}") or 1.0)
                        lora_list.extend([(lora_name, weight, weight)])
                    else:
                        model_weight = float(kwargs.get(f"model_weight_{i}") or 1.0)
                        clip_weight = float(kwargs.get(f"clip_weight_{i}") or 1.0)
                        lora_list.extend([(lora_name, model_weight, clip_weight)])

            return (lora_list,)


    ```

## LoraStack

Creates a configurable stack of up to 3 LoRA models with adjustable weights.

Provides a user interface to enable/disable and configure up to three LoRA models with independent
weights for both model and CLIP components. Can extend an existing LORA_STACK.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | switch_1 | `LIST` |  |  |
| required | lora_name_1 | `loras` |  |  |
| required | model_weight_1 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| required | clip_weight_1 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| required | switch_2 | `LIST` |  |  |
| required | lora_name_2 | `loras` |  |  |
| required | model_weight_2 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| required | clip_weight_2 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| required | switch_3 | `LIST` |  |  |
| required | lora_name_3 | `loras` |  |  |
| required | model_weight_3 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| required | clip_weight_3 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| optional | lora_stack | `LORA_STACK` |  |  |

### Returns

| Name | Type |
|------|------|
| lora_stack | `LORA_STACK` |


??? note "Source code"

    ```python
    class LoraStacker:
        """Manages multiple LoRA models with configurable weights and modes.

        This node provides an interface for stacking multiple LoRA models with independent
        weight controls and two operating modes for simple or advanced weight management.

        Args:
            num_slots (str): Number of LoRA slots to enable (1-10)
            mode (str): Weight control mode:
                - "Simple": Single weight per LoRA
                - "Advanced": Separate model and CLIP weights
            switch_1..10 (str): "On"/"Off" toggle for each LoRA slot
            lora_name_1..10 (str): Name of LoRA model for each slot
            weight_1..10 (float): Weight value for simple mode (-10.0 to 10.0)
            model_weight_1..10 (float): Model weight for advanced mode (-10.0 to 10.0)
            clip_weight_1..10 (float): CLIP weight for advanced mode (-10.0 to 10.0)
            lora_stack (LORA_STACK, optional): Existing stack to extend

        Returns:
            tuple[LORA_STACK]: Single-element tuple containing list of configured LoRAs

        Notes:
            - Each slot can be independently enabled/disabled
            - Simple mode uses same weight for model and CLIP
            - Advanced mode allows separate model and CLIP weights
            - Weights can be negative for inverse effects
            - Can extend existing LORA_STACK
            - Disabled or empty slots are skipped
        """

        @classmethod
        def INPUT_TYPES(cls):
            loras = ["None"] + folder_paths.get_filename_list("loras")

            inputs = {
                "required": {
                    "num_slots": ([str(i) for i in range(1, 11)], {"default": "1"}),
                    "mode": (["Simple", "Advanced"],),
                },
                "optional": {"lora_stack": ("LORA_STACK",)},
            }

            for i in range(1, 11):
                inputs["optional"].update(
                    {
                        f"switch_{i}": (["On", "Off"],),
                        f"lora_name_{i}": (loras,),
                        f"weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                        f"model_weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                        f"clip_weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    }
                )

            return inputs

        RETURN_TYPES = ("LORA_STACK",)
        RETURN_NAMES = ("lora_stack",)
        FUNCTION = "execute"
        CATEGORY = LABS_CAT
        CLASS_ID = "lora_stacker"

        def execute(self, **kwargs):
            num_slots = int(kwargs.get("num_slots", 3))
            mode = kwargs.get("mode", "Simple")
            lora_stack = kwargs.get("lora_stack")

            lora_list: list = []
            if lora_stack is not None:
                lora_list.extend([l for l in lora_stack if l[0] is not None and l[0] != ""])

            for i in range(1, num_slots + 1):
                switch = kwargs.get(f"switch_{i}")
                lora_name = kwargs.get(f"lora_name_{i}") or "None"

                if lora_name is not None and lora_name != "None" and switch == "On":
                    if mode == "Simple":
                        weight = float(kwargs.get(f"weight_{i}") or 1.0)
                        lora_list.extend([(lora_name, weight, weight)])
                    else:
                        model_weight = float(kwargs.get(f"model_weight_{i}") or 1.0)
                        clip_weight = float(kwargs.get(f"clip_weight_{i}") or 1.0)
                        lora_list.extend([(lora_name, model_weight, clip_weight)])

            return (lora_list,)


    class LoraStack:
        """Creates a configurable stack of up to 3 LoRA models with adjustable weights.

        Provides a user interface to enable/disable and configure up to three LoRA models with independent
        weights for both model and CLIP components. Can extend an existing LORA_STACK.

        Args:
            switch_1/2/3 (str): "On" or "Off" to enable/disable each LoRA
            lora_name_1/2/3 (str): Names of LoRA models to use
            model_weight_1/2/3 (float): Weight multipliers for model component (-10.0 to 10.0)
            clip_weight_1/2/3 (float): Weight multipliers for CLIP component (-10.0 to 10.0)
            lora_stack (LORA_STACK, optional): Existing stack to extend

        Returns:
            tuple:
                - LORA_STACK: List of tuples (lora_name, model_weight, clip_weight)

        Notes:
            - Each LoRA can be independently enabled/disabled
            - Weights can be negative for inverse effects
            - Only enabled LoRAs with valid names (not "None") are included in output
        """

        @classmethod
        def INPUT_TYPES(cls):
            loras = ["None"] + folder_paths.get_filename_list("loras")

            return {
                "required": {
                    "switch_1": (["Off", "On"],),
                    "lora_name_1": (loras,),
                    "model_weight_1": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    "clip_weight_1": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    "switch_2": (["Off", "On"],),
                    "lora_name_2": (loras,),
                    "model_weight_2": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    "clip_weight_2": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    "switch_3": (["Off", "On"],),
                    "lora_name_3": (loras,),
                    "model_weight_3": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    "clip_weight_3": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                },
                "optional": {"lora_stack": ("LORA_STACK",)},
            }

        RETURN_TYPES = ("LORA_STACK",)
        RETURN_NAMES = ("lora_stack",)
        FUNCTION = "execute"
        CATEGORY = LORA_CAT
        CLASS_NAME = "LoraStack(OLD)"
        DEPRECATED = True

        def execute(
            self,
            **kwargs,
        ):
            switch_1 = kwargs.get("switch_1")
            lora_name_1 = kwargs.get("lora_name_1")
            model_weight_1 = kwargs.get("model_weight_1")
            clip_weight_1 = kwargs.get("clip_weight_1")
            switch_2 = kwargs.get("switch_2")
            lora_name_2 = kwargs.get("lora_name_2")
            model_weight_2 = kwargs.get("model_weight_2")
            clip_weight_2 = kwargs.get("clip_weight_2")
            switch_3 = kwargs.get("switch_3")
            lora_name_3 = kwargs.get("lora_name_3")
            model_weight_3 = kwargs.get("model_weight_3")
            clip_weight_3 = kwargs.get("clip_weight_3")
            lora_stack = kwargs.get("lora_stack")

            lora_list: list = []
            if lora_stack is not None:
                lora_list.extend([l for l in lora_stack if l[0] != "None"])

            if lora_name_1 != "None" and switch_1 == "On":
                (lora_list.extend([(lora_name_1, model_weight_1, clip_weight_1)]),)  # type: ignore

            if lora_name_2 != "None" and switch_2 == "On":
                (lora_list.extend([(lora_name_2, model_weight_2, clip_weight_2)]),)  # type: ignore

            if lora_name_3 != "None" and switch_3 == "On":
                (lora_list.extend([(lora_name_3, model_weight_3, clip_weight_3)]),)  # type: ignore

            return (lora_list,)


    ```

## Dict2LoraStack

Converts a list of LoRA configuration dictionaries into a LORA_STACK format.

Transforms a list of dictionaries containing LoRA configurations into the tuple format required
for LORA_STACK operations. Can optionally extend an existing stack.

### Returns

| Name | Type |
|------|------|
| lora_stack | `LORA_STACK` |


??? note "Source code"

    ```python
    class Dict2LoraStack:
        """Converts a list of LoRA configuration dictionaries into a LORA_STACK format.

        Transforms a list of dictionaries containing LoRA configurations into the tuple format required
        for LORA_STACK operations. Can optionally extend an existing stack.

        Args:
            lora_dicts (LIST): List of dictionaries, each containing:
                - lora_name (str): Name of the LoRA model
                - lora_weight (float): Weight to apply to both model and CLIP
            lora_stack (LORA_STACK, optional): Existing stack to extend

        Returns:
            tuple:
                - LORA_STACK: List of tuples (lora_name, model_weight, clip_weight)

        Raises:
            ValueError: If lora_dicts is not a list

        Notes:
            - Uses same weight for both model and CLIP components
            - Filters out any "None" entries when extending existing stack
        """

        @classmethod
        def INPUT_TYPES(cls):
            inputs = {
                "required": {
                    "lora_dicts": ("LIST",),
                },
                "optional": {"lora_stack": ("LORA_STACK",)},
            }

            inputs["optional"] = {"lora_stack": ("LORA_STACK",)}
            return inputs

        RETURN_TYPES = ("LORA_STACK",)
        RETURN_NAMES = ("lora_stack",)
        FUNCTION = "execute"
        CATEGORY = LORA_CAT
        CLASS_ID = "dict_to_lora_stack"

        def execute(self, **kwargs):
            lora_dicts = kwargs.get("lora_dicts")
            if not isinstance(lora_dicts, list):
                raise ValueError("Lora dicts must be a list")
            lora_stack = kwargs.get("lora_stack")
            loras = [None for _ in lora_dicts]

            for idx, lora_dict in enumerate(lora_dicts):
                loras[idx] = (lora_dict["lora_name"], lora_dict["lora_weight"], lora_dict["lora_weight"])  # type: ignore

            # If lora_stack is not None, extend the loras list with lora_stack
            if lora_stack is not None:
                loras.extend([l for l in lora_stack if l[0] != "None"])

            return (loras,)


    ```

## SaveLoraCaptions

Saves images and captions in a format suitable for LoRA training.

Creates a structured dataset directory containing images and their corresponding caption files,
with support for multiple captions and optional text modifications.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | dataset_name | `STRING` |  |  |
| required | repeats | `INT` | 5 | min=1 |
| required | images | `IMAGE` |  |  |
| required | labels | `STRING` |  | forceInput=True |
| optional | prefix | `STRING` |  |  |
| optional | suffix | `STRING` |  |  |

### Returns

| Name | Type |
|------|------|
| string | `STRING` |


??? note "Source code"

    ```python
    class SaveLoraCaptions:
        """Saves images and captions in a format suitable for LoRA training.

        Creates a structured dataset directory containing images and their corresponding caption files,
        with support for multiple captions and optional text modifications.

        Args:
            dataset_name (str): Name for the dataset folder
            repeats (int): Number of times to repeat the dataset (min: 1)
            images (IMAGE): Tensor containing the images to save
            labels (str): Caption text, multiple captions separated by newlines
            prefix (str, optional): Text to add before each caption
            suffix (str, optional): Text to add after each caption

        Returns:
            tuple:
                - str: Path to the created dataset folder

        Raises:
            ValueError: If any input parameters are of incorrect type

        Notes:
            - Creates folder structure: comfy/loras_datasets/dataset_name_uuid/repeats_dataset_name/
            - Saves images as PNG files with corresponding .txt caption files
            - Supports multiple captions via newline separation
            - Includes UUID in folder name for uniqueness
            - Creates parent directories if they don't exist
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "dataset_name": ("STRING", {"default": ""}),
                    "repeats": ("INT", {"default": 5, "min": 1}),
                    "images": ("IMAGE",),
                    "labels": ("STRING", {"forceInput": True}),
                },
                "optional": {
                    "prefix": ("STRING", {"default": ""}),
                    "suffix": ("STRING", {"default": ""}),
                },
            }

        RETURN_TYPES = ("STRING",)
        RETURN_NAMES = ("folder_path",)
        OUTPUT_NODE = True
        FUNCTION = "execute"
        CATEGORY = LORA_CAT

        def execute(
            self,
            **kwargs,
        ):
            dataset_name = kwargs.get("dataset_name")
            if not isinstance(dataset_name, str):
                raise ValueError("Dataset name must be a string")
            repeats = kwargs.get("repeats")
            if not isinstance(repeats, int):
                raise ValueError("Repeats must be an integer")
            images = kwargs.get("images")
            if not isinstance(images, torch.Tensor):
                raise ValueError("Images must be a torch.Tensor")
            labels = kwargs.get("labels")
            if not isinstance(labels, str):
                raise ValueError("Labels must be a string")
            prefix = kwargs.get("prefix")
            if not isinstance(prefix, str):
                raise ValueError("Prefix must be a string")
            suffix = kwargs.get("suffix")
            if not isinstance(suffix, str):
                raise ValueError("Suffix must be a string")

            labels_list = labels.split("\n") if "\n" in labels else [labels]

            root_folder = os.path.join(BASE_COMFY_DIR, "loras_datasets")
            if not os.path.exists(root_folder):
                os.mkdir(root_folder)

            uuid = uuid7str()
            dataset_folder = os.path.join(root_folder, f"{dataset_name}_{uuid}")
            if not os.path.exists(dataset_folder):
                os.mkdir(dataset_folder)
            images_folder = os.path.join(dataset_folder, f"{repeats}_{dataset_name}")
            if not os.path.exists(images_folder):
                os.mkdir(images_folder)

            tensor_images = TensorImage.from_BWHC(images)
            for i, img in enumerate(tensor_images):
                # timestamp to be added to the image name

                TensorImage(img).save(os.path.join(images_folder, f"{dataset_name}_{i}.png"))
                # write txt label with the same name of the image
                with open(os.path.join(images_folder, f"{dataset_name}_{i}.txt"), "w") as f:
                    label = prefix + labels_list[i % len(labels_list)] + suffix
                    f.write(label)

            return (dataset_folder,)

    ```
