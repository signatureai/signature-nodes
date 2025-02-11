import torch
from comfy_execution.graph import ExecutionBlocker  # type: ignore
from comfy_execution.graph_utils import GraphBuilder, is_link  # type: ignore

from .categories import LABS_CAT, LOGIC_CAT
from .shared import ByPassTypeTuple, any_type

MAX_FLOW_NUM = 10


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
                "on_true": (any_type, {"lazy": True}),
                "on_false": (any_type, {"lazy": True}),
                "condition": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    FUNCTION = "execute"
    CATEGORY = LOGIC_CAT

    def check_lazy_status(self, condition: bool, on_true: any = None, on_false: any = None) -> any:
        if condition and on_true is None:
            return ["on_true"]
        if not condition and on_false is None:
            return ["on_false"]
        return None

    def execute(self, on_true: any, on_false: any, condition: bool = True) -> tuple[any]:
        return (on_true if condition else on_false,)


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

    def execute(self, should_continue: bool = False, input: any = None) -> tuple[any]:
        return (input if should_continue else ExecutionBlocker(None),)


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

    def execute(self, a: any, b: any, comparison: str = "a == b") -> tuple[bool]:
        try:
            output = self.COMPARE_FUNCTIONS[comparison](a, b)
        except Exception as e:
            if isinstance(a, torch.Tensor) and isinstance(b, torch.Tensor):
                output = self.COMPARE_FUNCTIONS[comparison](a.shape, b.shape)
            elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
                output = self.COMPARE_FUNCTIONS[comparison](len(a), len(b))
            else:
                raise e

        if isinstance(output, torch.Tensor):
            output = output.all().item()
        elif isinstance(output, (list, tuple)):
            output = all(output)

        return (bool(output),)


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
