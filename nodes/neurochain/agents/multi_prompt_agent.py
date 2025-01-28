import json
from typing import Any, Optional

from ...categories import AGENT_CAT


class MultiPromptAgent:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"prompts": ("LIST", {}), "agent": ("AGENT", {})}}

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("responses",)
    FUNCTION = "process"
    CATEGORY = AGENT_CAT
    OUTPUT_NODE = True

    def process(self, prompts: list, agent):
        results: list[Optional[dict[str, Any]]] = [None for _ in range(len(prompts))]
        for idx, prompt in enumerate(prompts):
            model_resp, metadata = agent.predict(prompt)
            results[idx] = {"prompt": prompt, "response": json.loads(model_resp), "metadata": metadata}
            print(model_resp)
        return (results,)
