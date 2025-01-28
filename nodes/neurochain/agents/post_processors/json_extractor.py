from neurochain.agents.resp_postprocessors.json_extractor import extract_json

from ....categories import AGENT_RESPONSE_POST_PROCESS_CAT


class JsonExtractor:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("FUNCTION",)
    RETURN_NAMES = ("post_processor",)
    FUNCTION = "process"
    CATEGORY = AGENT_RESPONSE_POST_PROCESS_CAT
    OUTPUT_NODE = True

    def process(self):
        return (extract_json,)
