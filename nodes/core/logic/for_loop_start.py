from comfy_execution.graph_utils import GraphBuilder  # type: ignore

from ...categories import LABS_CAT
from ...shared import ByPassTypeTuple, any_type
from .shared import MAX_FLOW_NUM


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

    def execute(self, **kwargs):
        current_index = 0
        if "init_value_0" in kwargs:
            current_index = kwargs["init_value_0"]

        graph = GraphBuilder()
        initial_values = {(f"init_value_{i}"): kwargs.get(f"init_value_{i}", None) for i in range(1, MAX_FLOW_NUM)}
        graph.node("signature_do_while_loop_start", init_value_0=current_index, **initial_values)
        outputs = [kwargs.get(f"init_value_{i}", None) for i in range(1, MAX_FLOW_NUM)]
        return {
            "result": tuple(["stub", current_index] + outputs),
            "expand": graph.finalize(),
        }
