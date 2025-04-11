from typing import Optional

from neurochain.evaluation.geval import Geval

from ...categories import EVALUATION_CAT

DEFAULT_EVALUATION_STEPS = """Read the input document carefully and identify the main topic and key points. The output \
must be a summary of the input document.
Check if the output covers the main topic and key points of the input document.
Check if the output presents the main topics of the input document in a clear and logical order.
Check if the output contains any factual errors that are not supported by the input document.
Check the quality of the output in terms of grammar, spelling, punctuation, word choice, and sentence structure.
Assess how much irrelevant or redundant information the output contains."""


class GevalEvaluation:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "criteria": ("STRING", {"default": ""}),
                "evaluation_steps": (
                    "STRING",
                    {"default": DEFAULT_EVALUATION_STEPS, "multiline": True},
                ),
            },
        }

    RETURN_TYPES = ("EVALUATOR",)
    FUNCTION = "process"
    CATEGORY = EVALUATION_CAT
    OUTPUT_NODE = True

    def process(self, evaluation_steps: Optional[str], criteria: Optional[str]):
        neurochain_criteria = criteria.strip() if criteria else None
        neurochain_evaluation_steps = None
        if neurochain_criteria is None or neurochain_criteria == "":
            neurochain_evaluation_steps = evaluation_steps.split("\n") if evaluation_steps else None
        evaluator = Geval(neurochain_criteria, neurochain_evaluation_steps)
        return (evaluator,)
