from neurochain.agents.orchestrator_embedding import (
    OrchestratorEmbedding as OrchestratorEmbeddingNode,
)
from weaviate import Client

from ...categories import AGENT_CAT


class OrchestratorEmbedding:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_url": ("STRING", {"default": "https://etudes.signature.ai"}),
                "weaviate_client": ("Client", {}),
                "tenant_id": ("STRING", {"default": "test"}),
                "tools": ("LIST",),
            },
            "optional": {
                "prompt": ("STRING", {"multiline": True}),
                "name": ("STRING", {"default": "Agent"}),
                "description": ("STRING", {"multiline": True, "default": "An agent that can answer various prompts."}),
            },
        }

    RETURN_TYPES = ("STRING", "DICT", "AGENT")
    RETURN_NAMES = ("response", "metadata", "agent")
    FUNCTION = "process"
    CATEGORY = AGENT_CAT
    OUTPUT_NODE = True

    def process(
        self,
        api_url: str,
        weaviate_client: Client,
        tenant_id: str,
        tools: list,
        prompt: str,
        name: str,
        description: str,
    ):
        orch = OrchestratorEmbeddingNode(
            api_url=api_url, client=weaviate_client, tenant_id=tenant_id, name=name, description=description
        )

        for tool in tools:
            # TODO - check if tool is a function
            orch.link(tool)

        if prompt == "undefined":
            return (
                None,
                None,
                orch,
            )

        orch_tool = orch.build()
        model_resp = orch_tool.run(prompt)
        return (
            model_resp,
            "{}",
            orch,
        )
