from neurochain.evaluation.bias import Bias

from ...categories import EVALUATION_CAT


class BiasEvaluation:
    @classmethod
    def INPUT_TYPES(cls):
        return {}

    RETURN_TYPES = ("EVALUATOR",)
    FUNCTION = "process"
    CATEGORY = EVALUATION_CAT
    OUTPUT_NODE = True

    def process(self):
        evaluator = Bias()
        return (evaluator,)
