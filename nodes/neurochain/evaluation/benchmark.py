import json
import os

import pandas as pd
from datasets import load_dataset
from neurochain.agents.classifier import Classifier
from neurochain.llms.gptq_model_exp import GPTQModelEXP
from neurochain.llms.ollama_llm import OllamaLLM
from neurochain.utils.utils import init_weaviate
from tqdm import tqdm

from ...categories import EVALUATION_CAT


class Benchmark:
    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "dataset_name": ("STRING", {"default": "financial_phrasebank"}),
                "revision": ("STRING", {"default": "sentences_allagree"}),
                "split": ("STRING", {"default": "train"}),
                "classifier": ("Classifier", {}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Classification", "DEBUG - LLM Thought")
    FUNCTION = "process"
    CATEGORY = EVALUATION_CAT
    OUTPUT_NODE = True

    def process(self, dataset_name, revision, split, classifier: Classifier):
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
        WEAVIATE_URL = os.environ.get("WEAVIATE_URL", "http://54.216.7.223:10600")
        WEBSERVICE_URL: str = os.environ.get("SERVER_URL", "https://etudes.signature.ai")
        ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "dev")

        if ENVIRONMENT == "dev":
            llm = OllamaLLM()
        else:
            llm = GPTQModelEXP(uri="ws://54.75.240.180:9997/api/v1/stream")

        client, retriever = init_weaviate(WEAVIATE_URL, OPENAI_API_KEY, k=1)

        dataset = load_dataset(dataset_name, revision, split=split)

        classes = [
            {"name": "Negative", "description": "", "id": "0"},
            {"name": "Neutral", "description": "", "id": "1"},
            {"name": "Positive", "description": "", "id": "2"},
        ]

        classifier = Classifier(
            name="classifier_test",
            llm=llm,
            api_url=WEBSERVICE_URL,
            client=client,
            retriever=retriever,
            tenant_id="test",
            classes=classes,
        )

        exp_log_df = pd.DataFrame(columns=["prompt", "ground_truth", "predicted", "llm_thought", "correct"])
        total = 0
        num_correct = 0
        accuracy = 0

        loop_obj = tqdm(
            range(len(dataset)),
            desc=f"Accuracy: {round(accuracy, 4)} | Correct: {num_correct} | Total: {total} ",
        )

        for i in loop_obj:
            loop_obj.set_description(f"Accuracy: {round(accuracy, 4)} | Correct: {num_correct} | Total: {total} ")

            prompt = dataset[i]["sentence"]
            gt_label_id = int(dataset[i]["label"])
            gt_class = None
            for c in classes:
                if int(c["id"]) == gt_label_id:
                    gt_class = c

            classifier_resp, llm_thought = classifier.query_agent(prompt)
            pred_class = json.loads(classifier_resp)
            pred_label_id = int(pred_class["id"])

            if pred_label_id == gt_label_id:
                num_correct += 1

            total += 1
            accuracy = num_correct / total

            log_entry = pd.DataFrame.from_dict(
                {
                    "prompt": [prompt],
                    "ground_truth": [gt_class["name"]],
                    "predicted": [pred_class["name"]],
                    "llm_thought": [llm_thought],
                    "correct": [pred_label_id == gt_label_id],
                }
            )

            exp_log_df = pd.concat([exp_log_df, log_entry], ignore_index=True)

            if i % 10 == 0:
                exp_log_df.to_csv("exp_log5.csv", index=False)

        exp_log_df.to_csv("exp_log5.csv", index=False)
        return ("output",)
