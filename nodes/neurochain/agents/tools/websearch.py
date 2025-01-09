from neurochain.agents.tools.websearch import SerperTool

from ....categories import AGENT_TOOLS_CAT


class WebsearchTool:
    @classmethod
    def INPUT_TYPES(cls):
        return {}

    RETURN_TYPES = ("BaseAgentTool",)
    RETURN_NAMES = ("tool",)
    FUNCTION = "process"
    CATEGORY = AGENT_TOOLS_CAT
    OUTPUT_NODE = True

    def process(self):
        return (SerperTool(),)
