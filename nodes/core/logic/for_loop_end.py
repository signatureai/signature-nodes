from comfy_execution.graph_utils import GraphBuilder  # type: ignore

from ...categories import LABS_CAT
from ...shared import ByPassTypeTuple, any_type
from .shared import MAX_FLOW_NUM


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
