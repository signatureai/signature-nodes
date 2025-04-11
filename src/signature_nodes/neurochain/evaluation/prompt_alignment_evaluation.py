from neurochain.evaluation.prompt_alignment import PromptAlignment

from ...categories import EVALUATION_CAT


class PromptAlignmentEvaluation:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_instructions": (
                    "STRING",
                    {"multiline": True, "default": "Output a maximum of 50 words"},
                ),
            }
        }

    RETURN_TYPES = ("EVALUATOR",)
    FUNCTION = "process"
    CATEGORY = EVALUATION_CAT
    OUTPUT_NODE = True

    def process(self, prompt_instructions: str):
        prompt_instructions_neurochain = [
            instruction.strip() for instruction in prompt_instructions.split("\n") if instruction.strip()
        ]
        evaluator = PromptAlignment(prompt_instructions_neurochain)
        return (evaluator,)
