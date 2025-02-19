from typing import Optional

from ...categories import LORA_CAT


class Dict2LoraStack:
    """Converts a list of LoRA configuration dictionaries into a LORA_STACK format.

    Transforms a list of dictionaries containing LoRA configurations into the tuple format required
    for LORA_STACK operations. Can optionally extend an existing stack.

    Args:
        lora_dicts (LIST): List of dictionaries, each containing:
            - lora_name (str): Name of the LoRA model
            - lora_weight (float): Weight to apply to both model and CLIP
        lora_stack (LORA_STACK, optional): Existing stack to extend

    Returns:
        tuple:
            - LORA_STACK: List of tuples (lora_name, model_weight, clip_weight)

    Raises:
        ValueError: If lora_dicts is not a list

    Notes:
        - Uses same weight for both model and CLIP components
        - Filters out any "None" entries when extending existing stack
    """

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "lora_dicts": ("LIST",),
            },
            "optional": {"lora_stack": ("LORA_STACK",)},
        }
        return inputs

    RETURN_TYPES = ("LORA_STACK",)
    FUNCTION = "execute"
    CATEGORY = LORA_CAT
    CLASS_ID = "dict_to_lora_stack"

    def execute(self, lora_dicts: list, lora_stack: Optional[list] = None):
        loras: list[Optional[tuple]] = [None for _ in lora_dicts]

        for idx, lora_dict in enumerate(lora_dicts):
            loras[idx] = (
                lora_dict["lora_name"],
                lora_dict["lora_weight"],
                lora_dict["lora_weight"],
            )  # type: ignore

        # If lora_stack is not None, extend the loras list with lora_stack
        if lora_stack is not None:
            loras.extend([lora for lora in lora_stack if lora[0] != "None"])

        return (loras,)
