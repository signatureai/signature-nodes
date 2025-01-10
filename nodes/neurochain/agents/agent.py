import uuid
from typing import Optional

import torch
from neurochain.agents.agent_new import AgentNew as AgentNewNeurochain
from neurochain.agents.tools.entities import BaseAgentTool
from neurochain.llms.entities import BaseLLM
from neurochain.memory.entities import BaseMemory
from signature_core.img.tensor_image import TensorImage

from ...categories import AGENT_CAT


class Agent:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "llm": ("BaseLLM", {}),
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "tools": ("LIST", {}),
                "images": ("LIST", {}),
                "memory": ("BaseMemory", {}),
                "system": ("STRING", {"default": "", "multiline": True}),
                "json_schema": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = (
        "STRING",
        "AGENT",
    )
    RETURN_NAMES = (
        "response",
        "agent",
    )
    FUNCTION = "process"
    CATEGORY = AGENT_CAT
    OUTPUT_NODE = True
    conversation_id = uuid.uuid4()

    def process(
        self,
        llm: BaseLLM,
        prompt: str,
        tools: Optional[list[BaseAgentTool]] = None,
        images: Optional[list[torch.Tensor]] = None,
        memory: Optional[BaseMemory] = None,
        system: Optional[str] = None,
        json_schema: Optional[str] = None,
    ) -> tuple:
        base64_images = None
        if images:
            base64_images = [TensorImage.from_BWHC(image).get_base64() for image in images]

        neurochain_system = system
        if neurochain_system:
            neurochain_system = neurochain_system.strip()
            if neurochain_system == "":
                neurochain_system = None

        agent = AgentNewNeurochain(
            llm=llm,
            tools=tools,
            system=neurochain_system,
            memory=memory,
            json_schema=json_schema,
        )
        response = agent.execute(prompt, images=base64_images, conversation_id=str(self.conversation_id))
        return (
            response,
            agent,
        )
