from neurochain.evaluation.summarization import Summarization

from ...categories import EVALUATION_CAT


class SummarizationEvaluation:
    @classmethod
    def INPUT_TYPES(cls):
        return {}

    RETURN_TYPES = ("EVALUATOR",)
    FUNCTION = "process"
    CATEGORY = EVALUATION_CAT
    OUTPUT_NODE = True

    def process(self):
        evaluator = Summarization()
        return (evaluator,)
