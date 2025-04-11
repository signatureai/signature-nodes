from typing import Optional

from neurochain.agents.classifier import Classifier as ClassifierNode
from neurochain.llms.gptq_model_exp import GPTQModelEXP
from neurochain.llms.ollama_llm import OllamaLLM
from neurochain.utils.utils import init_weaviate

from ...categories import AGENT_CAT
from ...env import env


class Classifier:
    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "name": ("STRING", {"default": ""}),
                "prompt": ("STRING", {"multiline": True, "default": "jdhasgdygasdygasy"}),
                "category_1": ("STRING", {"default": ""}),
                "description_1": ("STRING", {"multiline": True}),
                "category_2": ("STRING", {"default": ""}),
                "description_2": ("STRING", {"multiline": True}),
            },
            "optional": {
                "category_3": ("STRING", {"default": ""}),
                "description_3": ("STRING", {"multiline": True}),
                "category_4": ("STRING", {"default": ""}),
                "description_4": ("STRING", {"multiline": True}),
                "category_5": ("STRING", {"default": ""}),
                "description_5": ("STRING", {"multiline": True}),
                "category_6": ("STRING", {"default": ""}),
                "description_6": ("STRING", {"multiline": True}),
                "category_7": ("STRING", {"default": ""}),
                "description_7": ("STRING", {"multiline": True}),
                "category_8": ("STRING", {"default": ""}),
                "description_8": ("STRING", {"multiline": True}),
                "category_9": ("STRING", {"default": ""}),
                "description_9": ("STRING", {"multiline": True}),
                "category_10": ("STRING", {"default": ""}),
                "description_10": ("STRING", {"multiline": True}),
                "category_11": ("STRING", {"default": ""}),
                "description_11": ("STRING", {"multiline": True}),
                "category_12": ("STRING", {"default": ""}),
                "description_12": ("STRING", {"multiline": True}),
                "category_13": ("STRING", {"default": ""}),
                "description_13": ("STRING", {"multiline": True}),
                "category_14": ("STRING", {"default": ""}),
                "description_14": ("STRING", {"multiline": True}),
                "category_15": ("STRING", {"default": ""}),
                "description_15": ("STRING", {"multiline": True}),
                "category_16": ("STRING", {"default": ""}),
                "description_16": ("STRING", {"multiline": True}),
                "category_17": ("STRING", {"default": ""}),
                "description_17": ("STRING", {"multiline": True}),
                "category_18": ("STRING", {"default": ""}),
                "description_18": ("STRING", {"multiline": True}),
                "category_19": ("STRING", {"default": ""}),
                "description_19": ("STRING", {"multiline": True}),
                "category_20": ("STRING", {"default": ""}),
                "description_20": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "Classifier")
    RETURN_NAMES = ("Classification", "DEBUG - LLM Thought", "classifier")
    FUNCTION = "process"
    CATEGORY = AGENT_CAT
    OUTPUT_NODE = True

    def process(
        self,
        name: str,
        prompt: str,
        category_1: str,
        description_1: str,
        category_2: str,
        description_2: str,
        category_3: Optional[list] = None,
        description_3: Optional[list] = None,
        category_4: Optional[list] = None,
        description_4: Optional[list] = None,
        category_5: Optional[list] = None,
        description_5: Optional[list] = None,
        category_6: Optional[list] = None,
        description_6: Optional[list] = None,
        category_7: Optional[list] = None,
        description_7: Optional[list] = None,
        category_8: Optional[list] = None,
        description_8: Optional[list] = None,
        category_9: Optional[list] = None,
        description_9: Optional[list] = None,
        category_10: Optional[list] = None,
        description_10: Optional[list] = None,
        category_11: Optional[list] = None,
        description_11: Optional[list] = None,
        category_12: Optional[list] = None,
        description_12: Optional[list] = None,
        category_13: Optional[list] = None,
        description_13: Optional[list] = None,
        category_14: Optional[list] = None,
        description_14: Optional[list] = None,
        category_15: Optional[list] = None,
        description_15: Optional[list] = None,
        category_16: Optional[list] = None,
        description_16: Optional[list] = None,
        category_17: Optional[list] = None,
        description_17: Optional[list] = None,
        category_18: Optional[list] = None,
        description_18: Optional[list] = None,
        category_19: Optional[list] = None,
        description_19: Optional[list] = None,
        category_20: Optional[list] = None,
        description_20: Optional[list] = None,
    ):
        categories = [
            category_1,
            category_2,
            category_3,
            category_4,
            category_5,
            category_6,
            category_7,
            category_8,
            category_9,
            category_10,
            category_11,
            category_12,
            category_13,
            category_14,
            category_15,
            category_16,
            category_17,
            category_18,
            category_19,
            category_20,
        ]

        descriptions = [
            description_1,
            description_2,
            description_3,
            description_4,
            description_5,
            description_6,
            description_7,
            description_8,
            description_9,
            description_10,
            description_11,
            description_12,
            description_13,
            description_14,
            description_15,
            description_16,
            description_17,
            description_18,
            description_19,
            description_20,
        ]

        classes = []
        for idx, categ in enumerate(categories):
            if not categ == "":
                class_dict = {"name": categ, "description": descriptions[idx]}
                classes.append(class_dict)

        OPENAI_API_KEY = env.get("OPENAI_API_KEY")
        WEAVIATE_URL = env.get("WEAVIATE_URL")
        WEBSERVICE_URL: str = env.get("SERVER_URL")
        ENVIRONMENT: str = env.get("ENVIRONMENT")

        if ENVIRONMENT == "dev":
            llm = OllamaLLM()
        else:
            llm = GPTQModelEXP(host="ws://54.75.240.180:9997/api/v1/stream")

        client, retriever = init_weaviate(WEAVIATE_URL, OPENAI_API_KEY, k=1)

        classifier = ClassifierNode(
            name=name,
            # TODO: Use our new BaseLLM class here
            llm=llm,  # type: ignore
            api_url=WEBSERVICE_URL,
            client=client,
            retriever=retriever,
            tenant_id="test4",
            classes=classes,
        )
        classification, llm_thought = classifier.query_agent(prompt=prompt)
        return (classification, llm_thought, classifier)
