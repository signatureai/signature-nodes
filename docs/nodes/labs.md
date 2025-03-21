# Labs Nodes

## LoopStart

Initiates a loop with optional initial values for each iteration.

This node is deprecated. Use the "Do While Loop Start" node instead.

A control node that starts a loop, allowing for a specified number of iterations. It can accept
optional initial values for each iteration, which can be used within the loop. This node is useful
for creating iterative workflows where the same set of operations is performed multiple times.

??? note "Source code"

    ```python
    class LoopStart:
        """Initiates a loop with optional initial values for each iteration.

        This node is deprecated. Use the "Do While Loop Start" node instead.

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
        DEPRECATED = True

        CATEGORY = LABS_CAT + "/Loops"

        def execute(self, **kwargs):
            values = []
            for i in range(MAX_FLOW_NUM):
                values.append(kwargs.get(f"init_value_{i}", None))
            return tuple(["stub"] + values)


    ```

## LoopEnd

Ends a loop and returns the final values after the loop execution.

This node is deprecated. Use the "Do While Loop End" node instead.

A control node that signifies the end of a loop initiated by a `LoopStart` node. It processes the
flow control signal and can return the final values from the loop iterations. This node is useful
for managing the completion of iterative workflows and retrieving results after looping.

??? note "Source code"

    ```python
    class LoopEnd:
        """Ends a loop and returns the final values after the loop execution.

        This node is deprecated. Use the "Do While Loop End" node instead.

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
        DEPRECATED = True
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

        def execute(self, flow: tuple[str], end_loop: bool, dynprompt=None, unique_id=None, **kwargs):
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
                    node = graph.node(
                        original_node["class_type"],
                        "Recurse" if node_id == unique_id else node_id,
                    )
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

## OTSUThreshold

A node that performs Otsu's thresholding on an input image.

This node implements Otsu's method, which automatically determines an optimal threshold
value by minimizing intra-class intensity variance. It converts the input image to
grayscale and applies binary thresholding using the computed optimal threshold.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | image | `IMAGE` |  |  |

### Returns

| Name | Type |
|------|------|
| float | `FLOAT` |
| image | `IMAGE` |


??? note "Source code"

    ```python
    class OTSUThreshold:
        """A node that performs Otsu's thresholding on an input image.

        This node implements Otsu's method, which automatically determines an optimal threshold
        value by minimizing intra-class intensity variance. It converts the input image to
        grayscale and applies binary thresholding using the computed optimal threshold.

        Args:
            image (torch.Tensor): The input image tensor to threshold.
                                Expected shape: (B, H, W, C)

        Returns:
            tuple[float, torch.Tensor]: A tuple containing:
                - The computed Otsu threshold value
                - The thresholded binary image as a tensor with shape (B, H, W, C)

        Notes:
            - The input image is automatically converted to grayscale before thresholding
            - The output binary image contains values of 0 and 255
            - The threshold computation is performed using OpenCV's implementation
        """

        CLASS_ID = "otsu_threshold"
        CATEGORY = LABS_CAT

        @classmethod
        def INPUT_TYPES(cls):  # type: ignore
            return {
                "required": {
                    "image": ("IMAGE",),
                }
            }

        RETURN_TYPES = ("FLOAT", "IMAGE")
        FUNCTION = "execute"

        def execute(self, image: torch.Tensor) -> tuple[float, torch.Tensor]:
            img_transformed = v2.Compose(
                [
                    ops.Permute(dims=[0, 3, 1, 2]),
                    v2.Grayscale(),
                    v2.ToDtype(torch.uint8, scale=True),
                ]
            )(image)
            img_np = img_transformed.squeeze().cpu().numpy()

            thresh, out = cv.threshold(img_np, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

            out_torch = torch.from_numpy(out).to(image.device).unsqueeze(0).unsqueeze(0)
            out_transformed = v2.Compose([v2.RGB(), ops.Permute(dims=[0, 2, 3, 1])])(out_torch)
            return (thresh, out_transformed)
    ```

## ForLoopEnd

Ends a for loop and returns final values after all iterations.
    Works with ForLoopStart to create iterative workflows with a fixed number of iterations.
    Manages loop state and termination based on the iteration count.

??? note "Source code"

    ```python
    class ForLoopEnd:
        @classmethod
        def INPUT_TYPES(cls):
            inputs = {
                "required": {
                    "flow": ("FLOW_CONTROL", {"rawLink": True, "forceInput": True}),
                    "num_slots": ([str(i) for i in range(1, MAX_FLOW_NUM)], {"default": "1"}),
                },
                "optional": {},
                "hidden": {
                    "dynprompt": "DYNPROMPT",
                    "unique_id": "UNIQUE_ID",
                },
            }
            for i in range(1, MAX_FLOW_NUM):
                inputs["optional"][f"init_value_{i}"] = (any_type, {"rawLink": True, "forceInput": True})
            return inputs

        RETURN_TYPES = ByPassTypeTuple(tuple([any_type] * (MAX_FLOW_NUM - 1)))
        RETURN_NAMES = ByPassTypeTuple(tuple(f"value_{i}" for i in range(1, MAX_FLOW_NUM)))
        FUNCTION = "execute"
        CATEGORY = LABS_CAT + "/Loops"
        DESCRIPTION = """
        Ends a for loop and returns final values after all iterations.
        Works with ForLoopStart to create iterative workflows with a fixed number of iterations.
        Manages loop state and termination based on the iteration count.
        """

        def execute(self, flow: tuple[str], dynprompt=None, unique_id=None, **kwargs):
            graph = GraphBuilder()
            while_open = flow[0]
            iterations = 0

            if dynprompt is not None:
                forstart_node = dynprompt.get_node(while_open)
                inputs = forstart_node["inputs"]
                iterations = inputs["iterations"]

            mathAddOne = graph.node("signature_math_operator", value="a+1", a=[while_open, 1])
            condition = graph.node("signature_compare", a=mathAddOne.out(0), b=iterations, comparison="a >= b")

            input_values = {(f"init_value_{i}"): kwargs.get(f"init_value_{i}", None) for i in range(1, MAX_FLOW_NUM)}
            while_close = graph.node(
                "signature_do_while_loop_end",
                flow=flow,
                end_loop=condition.out(0),
                init_value_0=mathAddOne.out(0),
                **input_values,
            )

            return {
                "result": tuple([while_close.out(i) for i in range(1, MAX_FLOW_NUM)]),
                "expand": graph.finalize(),
            }
    ```

## DoWhileLoopEnd

Ends a loop and returns the final values after the loop execution.

A control node that signifies the end of a loop initiated by a `LoopStart` node. It processes the
flow control signal and can return the final values from the loop iterations. This node is useful
for managing the completion of iterative workflows and retrieving results after looping.

??? note "Source code"

    ```python
    class DoWhileLoopEnd:
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
                    "flow": ("FLOW_CONTROL", {"rawLink": True, "forceInput": True}),
                    "end_loop": ("BOOLEAN", {"forceInput": True}),
                    "num_slots": ([str(i) for i in range(1, MAX_FLOW_NUM + 1)], {"default": "1"}),
                },
                "optional": {},
                "hidden": {"dynprompt": "DYNPROMPT", "unique_id": "UNIQUE_ID"},
            }
            for i in range(MAX_FLOW_NUM):
                inputs["optional"][f"init_value_{i}"] = (any_type, {"forceInput": True})
            return inputs

        RETURN_TYPES = ByPassTypeTuple(tuple([any_type] * MAX_FLOW_NUM))
        RETURN_NAMES = ByPassTypeTuple(tuple(f"value_{i}" for i in range(MAX_FLOW_NUM)))
        FUNCTION = "execute"
        CATEGORY = LABS_CAT + "/Loops"
        DESCRIPTION = """
        Ends a do-while loop and returns final values after execution.
        Controls loop termination based on the 'end_loop' condition.
        Works with DoWhileLoopStart to create iterative workflows that execute at least once before checking the condition.
        """

        def explore_dependencies(self, node_id, dynprompt, upstream, parent_ids):
            node_info = dynprompt.get_node(node_id)
            if "inputs" not in node_info:
                return
            for _, v in node_info["inputs"].items():
                if is_link(v):
                    parent_id = v[0]
                    display_id = dynprompt.get_display_node_id(parent_id)
                    display_node = dynprompt.get_node(display_id)
                    class_type = display_node["class_type"]
                    if class_type not in ["signature_for_loop_end", "signature_do_while_loop_end"]:
                        parent_ids.append(display_id)
                    if parent_id not in upstream:
                        upstream[parent_id] = []
                        self.explore_dependencies(parent_id, dynprompt, upstream, parent_ids)

                    upstream[parent_id].append(node_id)

        def explore_output_nodes(self, dynprompt, upstream, output_nodes, parent_ids):
            for parent_id in upstream:
                display_id = dynprompt.get_display_node_id(parent_id)
                for output_id in output_nodes:
                    id = output_nodes[output_id][0]
                    if id in parent_ids and display_id == id and output_id not in upstream[parent_id]:
                        if "." in parent_id:
                            arr = parent_id.split(".")
                            arr[len(arr) - 1] = output_id
                            upstream[parent_id].append(".".join(arr))
                        else:
                            upstream[parent_id].append(output_id)

        def collect_contained(self, node_id, upstream, contained):
            if node_id not in upstream:
                return
            for child_id in upstream[node_id]:
                if child_id not in contained:
                    contained[child_id] = True
                    self.collect_contained(child_id, upstream, contained)

        def execute(self, flow: tuple[str], end_loop: bool, dynprompt=None, unique_id=None, **kwargs):
            if end_loop:
                # We're done with the loop
                values = []
                for i in range(MAX_FLOW_NUM):
                    values.append(kwargs.get(f"init_value_{i}", None))
                return tuple(values)

            # We want to loop
            if dynprompt is not None:
                dynprompt.get_node(unique_id)
            upstream = {}
            # Get the list of all nodes between the open and close nodes
            parent_ids = []
            self.explore_dependencies(unique_id, dynprompt, upstream, parent_ids)
            parent_ids = list(set(parent_ids))

            if dynprompt is not None:
                prompts = dynprompt.get_original_prompt()
            output_nodes = {}
            for id in prompts:
                node = prompts[id]
                if "inputs" not in node:
                    continue
                class_type = node["class_type"]
                class_def = ALL_NODE_CLASS_MAPPINGS[class_type]
                if hasattr(class_def, "OUTPUT_NODE") and class_def.OUTPUT_NODE:
                    for k, v in node["inputs"].items():
                        if is_link(v):
                            output_nodes[id] = v

            graph = GraphBuilder()
            self.explore_output_nodes(dynprompt, upstream, output_nodes, parent_ids)
            contained = {}
            open_node = flow[0]
            self.collect_contained(open_node, upstream, contained)
            contained[unique_id] = True
            contained[open_node] = True

            for node_id in contained:
                if dynprompt is not None:
                    original_node = dynprompt.get_node(node_id)
                    node = graph.node(
                        original_node["class_type"],
                        "Recurse" if node_id == unique_id else node_id,
                    )
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

## Blocker

Controls flow execution based on a boolean condition.

A utility node that blocks or allows execution flow based on a boolean flag. When the continue
flag is False, it blocks execution by returning an ExecutionBlocker. When True, it passes through
the input value unchanged.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | should_continue | `BOOLEAN` | False |  |
| required | input | `any_type` | None |  |

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
                    "should_continue": ("BOOLEAN", {"default": False}),
                    "input": (any_type, {"default": None}),
                },
            }

        RETURN_TYPES = (any_type,)
        RETURN_NAMES = ("out",)
        CATEGORY = LABS_CAT
        FUNCTION = "execute"
        DESCRIPTION = """
        Controls workflow execution based on a boolean condition.
        When 'should_continue' is False, blocks downstream execution by returning an ExecutionBlocker.
        When True, passes through the input value unchanged.
        Useful for conditional branches.
        """

        def execute(self, should_continue: bool = False, input: Any = None) -> tuple[Any]:
            return (input if should_continue else ExecutionBlocker(None),)
    ```

## ForLoopStart

Initiates a for loop with a specified number of iterations.
    Creates a loop that executes a fixed number of times, tracking the current iteration index.
    Works with ForLoopEnd to create iterative workflows with predictable execution counts.

??? note "Source code"

    ```python
    class ForLoopStart:
        @classmethod
        def INPUT_TYPES(cls):
            inputs = {
                "required": {
                    "iterations": ("INT", {"default": 1, "min": 1, "max": 100000, "step": 1}),
                    "num_slots": ([str(i) for i in range(1, MAX_FLOW_NUM)], {"default": "1"}),
                },
                "optional": {},
                "hidden": {
                    "init_value_0": (any_type,),
                },
            }
            for i in range(1, MAX_FLOW_NUM):
                inputs["optional"][f"init_value_{i}"] = (any_type, {"forceInput": True})
            return inputs

        RETURN_TYPES = ByPassTypeTuple(tuple(["FLOW_CONTROL", "INT"] + [any_type] * (MAX_FLOW_NUM - 1)))
        RETURN_NAMES = ByPassTypeTuple(tuple(["flow", "current_index"] + [f"value_{i}" for i in range(1, MAX_FLOW_NUM)]))
        FUNCTION = "execute"

        CATEGORY = LABS_CAT + "/Loops"
        DESCRIPTION = """
        Initiates a for loop with a specified number of iterations.
        Creates a loop that executes a fixed number of times, tracking the current iteration index.
        Works with ForLoopEnd to create iterative workflows with predictable execution counts.
        """

        def execute(self, **kwargs):
            current_index = 0
            if "init_value_0" in kwargs:
                current_index = kwargs["init_value_0"]

            graph = GraphBuilder()
            initial_values = {(f"init_value_{i}"): kwargs.get(f"init_value_{i}", None) for i in range(1, MAX_FLOW_NUM)}
            # TODO: check if signature_do_while_loop_start is the correct name, or if it should be signature_for_loop_start
            graph.node("signature_do_while_loop_start", init_value_0=current_index, **initial_values)
            outputs = [kwargs.get(f"init_value_{i}", None) for i in range(1, MAX_FLOW_NUM)]
            return {
                "result": tuple(["stub", current_index] + outputs),
                "expand": graph.finalize(),
            }
    ```

## DoWhileLoopStart

Initiates a loop with optional initial values for each iteration.

A control node that starts a loop, allowing for a specified number of iterations. It can accept
optional initial values for each iteration, which can be used within the loop. This node is useful
for creating iterative workflows where the same set of operations is performed multiple times. The
"Do While Loop End" node checks if the loop should continue, so this is a "do while" loop.

??? note "Source code"

    ```python
    class DoWhileLoopStart:
        """Initiates a loop with optional initial values for each iteration.

        A control node that starts a loop, allowing for a specified number of iterations. It can accept
        optional initial values for each iteration, which can be used within the loop. This node is useful
        for creating iterative workflows where the same set of operations is performed multiple times. The
        "Do While Loop End" node checks if the loop should continue, so this is a "do while" loop.

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
                "required": {
                    "num_slots": ([str(i) for i in range(1, MAX_FLOW_NUM + 1)], {"default": "1"}),
                },
                "optional": {},
            }
            for i in range(MAX_FLOW_NUM):
                inputs["optional"][f"init_value_{i}"] = (any_type, {"forceInput": True})
            return inputs

        RETURN_TYPES = ByPassTypeTuple(tuple(["FLOW_CONTROL"] + [any_type] * MAX_FLOW_NUM))
        RETURN_NAMES = ByPassTypeTuple(tuple(["flow"] + [f"value_{i}" for i in range(MAX_FLOW_NUM)]))
        FUNCTION = "execute"

        CATEGORY = LABS_CAT + "/Loops"
        DESCRIPTION = """
        Initiates a do-while loop with optional initial values.
        Starts an iterative workflow that executes at least once before checking a condition.
        Works with DoWhileLoopEnd to create loops that process the same operations multiple times.
        """

        def execute(self, **kwargs):
            values = []
            for i in range(MAX_FLOW_NUM):
                values.append(kwargs.get(f"init_value_{i}", None))
            return tuple(["stub"] + values)
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
                        f"weight_{i}": (
                            "FLOAT",
                            {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                        ),
                        f"model_weight_{i}": (
                            "FLOAT",
                            {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                        ),
                        f"clip_weight_{i}": (
                            "FLOAT",
                            {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                        ),
                    }
                )

            return inputs

        RETURN_TYPES = ("LORA_STACK",)
        RETURN_NAMES = ("lora_stack",)
        FUNCTION = "execute"
        CATEGORY = LABS_CAT
        CLASS_ID = "lora_stacker"
        DESCRIPTION = """
        Manages multiple LoRA models with configurable weights and modes.
        Provides an interface for stacking up to 10 LoRA models with independent weight controls.
        Supports simple mode (single weight) or advanced mode (separate model and CLIP weights).
        """

        def execute(self, **kwargs):
            num_slots = int(kwargs.get("num_slots", 1))
            mode = kwargs.get("mode", "Simple")
            lora_stack = kwargs.get("lora_stack")

            lora_list: list = []
            if lora_stack is not None:
                lora_list.extend([lora for lora in lora_stack if lora[0] is not None and lora[0] != ""])

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

## DINOHeatmap

A ComfyUI node that generates similarity heatmaps using DINO Vision Transformer.

This node takes an input image and a template image, optionally with a mask,
and produces a heatmap showing regions similar to the template using DINO embeddings.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | image | `IMAGE` |  |  |
| required | template | `IMAGE` |  |  |
| optional | mask | `MASK` |  |  |

### Returns

| Name | Type |
|------|------|
| image | `IMAGE` |


??? note "Source code"

    ```python
    class DINOHeatmap:
        """A ComfyUI node that generates similarity heatmaps using DINO Vision Transformer.

        This node takes an input image and a template image, optionally with a mask,
        and produces a heatmap showing regions similar to the template using DINO embeddings.
        """

        CLASS_ID = "dino_heatmap"
        CATEGORY = LABS_CAT
        DESCRIPTION = """Generates a similarity heatmap between two images using DINO Vision Transformer.

        This node helps you find regions in an image that are similar to a template image. It uses Facebook's DINOv2
        Vision Transformer model to analyze the images and create a heatmap highlighting matching areas.

        Inputs:
        - Image: The main image to analyze
        - Template: The reference image to search for
        - Mask (optional): A mask to focus the search on specific areas of the template. If provided, mask dimensions (H, W)
          should be equal to those of the template.

        Output:
        - A heatmap image where brighter areas indicate stronger similarity to the template

        When a mask is provided, the node will direct attention to specific regions of the template defined by the mask.
        If no mask is provided, the entire template will be considered for similarity matching.

        This is useful for:
        - Finding specific objects or patterns in images
        - Analyzing image composition and recurring elements
        - Visual pattern matching and comparison
        - Object localization without traditional object detection"""

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "image": ("IMAGE",),
                    "template": ("IMAGE",),
                },
                "optional": {
                    "mask": ("MASK",),
                },
            }

        RETURN_TYPES = ("IMAGE",)
        FUNCTION = "execute"

        def execute(self, image: Tensor, template: Tensor, mask: Optional[Tensor] = None) -> tuple[Tensor,]:
            image = TensorImage.from_BWHC(image)
            template = TensorImage.from_BWHC(template)
            mask = TensorImage.from_BWHC(mask) if mask is not None else None

            model = DINOSimilarity()
            output = model.predict(image, template, mask)

            output = TensorImage(output).get_BWHC()
            return (output,)

    ```
