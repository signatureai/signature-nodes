from neurochain.evaluation.summarization import Summarization

from ...categories import EVALUATION_CAT


class SummarizationEvaluation:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": ("STRING", {}),
                "output": ("STRING", {}),
            }
        }

    RETURN_TYPES = ("FLOAT", "STRING")
    RETURN_NAMES = ("score", "reason")
    FUNCTION = "process"
    CATEGORY = EVALUATION_CAT
    OUTPUT_NODE = True

    def process(self, input: str, output: str):
        evaluator = Summarization()
        evaluation_result = evaluator.evaluate(input, output)
        return (evaluation_result.score, evaluation_result.reason)
