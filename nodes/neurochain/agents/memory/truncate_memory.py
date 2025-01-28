from neurochain.agents.memory.internal_truncate_memory import InternalTruncateMemory

from ....categories import AGENT_MEMORY_CAT


class TruncateMemory:
    @classmethod
    def INPUT_TYPES(cls):
        return {}

    RETURN_TYPES = ("BaseMemory",)
    RETURN_NAMES = ("memory",)
    FUNCTION = "process"
    CATEGORY = AGENT_MEMORY_CAT
    OUTPUT_NODE = True

    def process(self) -> tuple:
        return (InternalTruncateMemory.create(),)
