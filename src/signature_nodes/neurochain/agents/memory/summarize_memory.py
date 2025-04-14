from neurochain.agents.memory.internal_summarize_memory import InternalSummarizeMemory
from neurochain.llms.entities import BaseLLM

from ....categories import AGENT_MEMORY_CAT


class SummarizeMemory:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm": ("BaseLLM", {}),
            }
        }

    RETURN_TYPES = ("BaseMemory",)
    RETURN_NAMES = ("memory",)
    FUNCTION = "process"
    CATEGORY = AGENT_MEMORY_CAT
    OUTPUT_NODE = True

    def process(self, llm: BaseLLM) -> tuple:
        return (InternalSummarizeMemory.create(llm),)
