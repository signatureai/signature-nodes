import uuid
from typing import Callable, Optional

import torch
from neurochain.agents.agent import Agent as AgentNeurochain
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
                "tools": ("LIST,AGENT_TOOL", {}),
                "images": ("LIST,IMAGE", {}),
                "memory": ("BaseMemory", {}),
                "system": ("STRING", {"default": "", "multiline": True}),
                "json_schema": ("STRING", {"default": "", "multiline": True}),
                "validators": ("LIST", {}),
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
        tools: Optional[list[BaseAgentTool] | BaseAgentTool] = None,
        images: Optional[list[torch.Tensor] | torch.Tensor] = None,
        memory: Optional[BaseMemory] = None,
        system: Optional[str] = None,
        json_schema: Optional[str] = None,
        validators: Optional[list[Callable[[str], bool]]] = None,
    ) -> tuple:
        base64_images = None
        if images is not None:
            if isinstance(images, list):
                base64_images = [TensorImage.from_BWHC(image).get_base64() for image in images]
            else:
                base64_images = [TensorImage.from_BWHC(images).get_base64()]

        neurochain_tools = None
        if tools:
            if isinstance(tools, list):
                neurochain_tools = tools
            else:
                neurochain_tools = [tools]

        neurochain_system = system
        if neurochain_system:
            neurochain_system = neurochain_system.strip()
            if neurochain_system == "":
                neurochain_system = None

        agent = AgentNeurochain(
            llm=llm,
            tools=neurochain_tools,
            system=neurochain_system,
            memory=memory,
            json_schema=json_schema,
            validators=validators,
        )
        response = agent.execute(prompt, images=base64_images, conversation_id=str(self.conversation_id))
        return (
            response,
            agent,
        )
