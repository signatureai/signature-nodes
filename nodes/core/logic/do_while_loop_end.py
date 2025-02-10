from comfy_execution.graph_utils import GraphBuilder, is_link  # type: ignore

from ...categories import LABS_CAT
from ...shared import ByPassTypeTuple, any_type

MAX_FLOW_NUM = 10


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
            "hidden": {
                "dynprompt": "DYNPROMPT",
                "unique_id": "UNIQUE_ID",
            },
        }
        for i in range(MAX_FLOW_NUM):
            inputs["optional"][f"init_value_{i}"] = (any_type, {"forceInput": True})
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
