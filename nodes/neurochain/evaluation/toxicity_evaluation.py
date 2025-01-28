from neurochain.evaluation.toxicity import Toxicity

from ...categories import EVALUATION_CAT


class ToxicityEvaluation:
    @classmethod
    def INPUT_TYPES(cls):
        return {}

    RETURN_TYPES = ("EVALUATOR",)
    FUNCTION = "process"
    CATEGORY = EVALUATION_CAT
    OUTPUT_NODE = True

    def process(self):
        evaluator = Toxicity()
        return (evaluator,)
