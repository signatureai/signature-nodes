from ...categories import LABS_CAT
from ...shared import ByPassTypeTuple, any_type

MAX_FLOW_NUM = 10


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
