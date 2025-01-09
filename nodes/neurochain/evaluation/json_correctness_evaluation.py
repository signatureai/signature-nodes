from neurochain.evaluation.json_correctness import JsonCorrectness

from ...categories import EVALUATION_CAT

DEFAULT_JSON_SCHEMA = """{
    "type": "object",
    "properties": {
        "score": {"type": "number"},
        "reason": {"type": "string"}
    },
    "required": ["score", "reason"]
}"""


class JsonCorrectnessEvaluation:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": ("STRING", {}),
                "json_schema": (
                    "STRING",
                    {"multiline": True, "default": DEFAULT_JSON_SCHEMA},
                ),
                "output": ("STRING", {}),
            }
        }

    RETURN_TYPES = ("FLOAT", "STRING")
    RETURN_NAMES = ("score", "reason")
    FUNCTION = "process"
    CATEGORY = EVALUATION_CAT
    OUTPUT_NODE = True

    def process(self, input: str, json_schema: str, output: str):
        evaluator = JsonCorrectness(json_schema)
        evaluation_result = evaluator.evaluate(input, output)
        return (evaluation_result.score, evaluation_result.reason)
