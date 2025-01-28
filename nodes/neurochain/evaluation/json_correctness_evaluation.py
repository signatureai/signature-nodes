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
                "json_schema": (
                    "STRING",
                    {"multiline": True, "default": DEFAULT_JSON_SCHEMA},
                ),
            }
        }

    RETURN_TYPES = ("EVALUATOR",)
    FUNCTION = "process"
    CATEGORY = EVALUATION_CAT
    OUTPUT_NODE = True

    def process(self, json_schema: str):
        evaluator = JsonCorrectness(json_schema)
        return (evaluator,)
