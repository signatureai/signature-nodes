from neurochain.evaluation.prompt_alignment import PromptAlignment

from ...categories import EVALUATION_CAT


class PromptAlignmentEvaluation:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": ("STRING", {}),
                "prompt_instructions": (
                    "STRING",
                    {"multiline": True, "default": "Output a maximum of 50 words"},
                ),
                "output": ("STRING", {}),
            }
        }

    RETURN_TYPES = ("FLOAT", "STRING")
    RETURN_NAMES = ("score", "reason")
    FUNCTION = "process"
    CATEGORY = EVALUATION_CAT
    OUTPUT_NODE = True

    def process(self, input: str, prompt_instructions: str, output: str):
        prompt_instructions_neurochain = [
            instruction.strip()
            for instruction in prompt_instructions.split("\n")
            if instruction.strip()
        ]
        evaluator = PromptAlignment(prompt_instructions_neurochain)
        evaluation_result = evaluator.evaluate(input, output)
        return (evaluation_result.score, evaluation_result.reason)
