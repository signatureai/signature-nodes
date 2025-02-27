from typing import Any, Optional

import folder_paths  # type: ignore
from comfy import sd, utils  # type: ignore

from ...categories import LORA_CAT


class ApplyLoraStack:
    """Applies multiple LoRA models sequentially to a base model and CLIP in ComfyUI.

    This node takes a base model, CLIP, and a stack of LoRA models as input. It applies each LoRA
    in the stack sequentially using specified weights for both model and CLIP components.

    Args:
        model (MODEL): The base Stable Diffusion model to modify
        clip (CLIP): The CLIP model to modify
        lora_stack (LORA_STACK): A list of tuples containing (lora_name, model_weight, clip_weight)

    Returns:
        tuple:
            - MODEL: The modified Stable Diffusion model with all LoRAs applied
            - CLIP: The modified CLIP model with all LoRAs applied

    Notes:
        - LoRAs are applied in sequence, with each modification building on previous changes
        - If lora_stack is None, returns the original model and CLIP unchanged
        - Uses ComfyUI's built-in LoRA loading and application mechanisms
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "lora_stack": ("LORA_STACK",),
            }
        }

    RETURN_TYPES = (
        "MODEL",
        "CLIP",
    )
    RETURN_NAMES = (
        "MODEL",
        "CLIP",
    )
    FUNCTION = "execute"
    CATEGORY = LORA_CAT
    DESCRIPTION = "Applies multiple LoRA models sequentially to a base model and CLIP. Processes each LoRA in the stack with specified weights for both model and CLIP components. Useful for combining multiple style or concept adaptations in a single workflow."

    def execute(
        self,
        model: Any,
        clip: Any,
        lora_stack: Optional[list] = None,
    ):
        if lora_stack is None:
            return (
                model,
                clip,
            )

        loras = []
        model_lora = model
        clip_lora = clip
        loras.extend(lora_stack)

        for lora in loras:
            lora_name, strength_model, strength_clip = lora

            lora_path = folder_paths.get_full_path("loras", lora_name)
            lora = utils.load_torch_file(lora_path, safe_load=True)

            model_lora, clip_lora = sd.load_lora_for_models(model_lora, clip_lora, lora, strength_model, strength_clip)

        return (
            model_lora,
            clip_lora,
        )
