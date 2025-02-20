import folder_paths  # type: ignore

from ...categories import LORA_CAT


class LoraStack:
    """Creates a configurable stack of up to 3 LoRA models with adjustable weights.

    Provides a user interface to enable/disable and configure up to three LoRA models with independent
    weights for both model and CLIP components. Can extend an existing LORA_STACK.

    Args:
        switch_1/2/3 (str): "On" or "Off" to enable/disable each LoRA
        lora_name_1/2/3 (str): Names of LoRA models to use
        model_weight_1/2/3 (float): Weight multipliers for model component (-10.0 to 10.0)
        clip_weight_1/2/3 (float): Weight multipliers for CLIP component (-10.0 to 10.0)
        lora_stack (LORA_STACK, optional): Existing stack to extend

    Returns:
        tuple:
            - LORA_STACK: List of tuples (lora_name, model_weight, clip_weight)

    Notes:
        - Each LoRA can be independently enabled/disabled
        - Weights can be negative for inverse effects
        - Only enabled LoRAs with valid names (not "None") are included in output
    """

    @classmethod
    def INPUT_TYPES(cls):
        loras = ["None"] + folder_paths.get_filename_list("loras")

        return {
            "required": {
                "switch_1": (["Off", "On"],),
                "lora_name_1": (loras,),
                "model_weight_1": (
                    "FLOAT",
                    {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                ),
                "clip_weight_1": (
                    "FLOAT",
                    {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                ),
                "switch_2": (["Off", "On"],),
                "lora_name_2": (loras,),
                "model_weight_2": (
                    "FLOAT",
                    {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                ),
                "clip_weight_2": (
                    "FLOAT",
                    {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                ),
                "switch_3": (["Off", "On"],),
                "lora_name_3": (loras,),
                "model_weight_3": (
                    "FLOAT",
                    {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                ),
                "clip_weight_3": (
                    "FLOAT",
                    {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                ),
            },
            "optional": {"lora_stack": ("LORA_STACK",)},
        }

    RETURN_TYPES = ("LORA_STACK",)
    RETURN_NAMES = ("lora_stack",)
    FUNCTION = "execute"
    CATEGORY = LORA_CAT
    CLASS_NAME = "LoraStack(OLD)"
    DEPRECATED = True

    def execute(
        self,
        **kwargs,
    ):
        switch_1 = kwargs.get("switch_1")
        lora_name_1 = kwargs.get("lora_name_1")
        model_weight_1 = kwargs.get("model_weight_1")
        clip_weight_1 = kwargs.get("clip_weight_1")
        switch_2 = kwargs.get("switch_2")
        lora_name_2 = kwargs.get("lora_name_2")
        model_weight_2 = kwargs.get("model_weight_2")
        clip_weight_2 = kwargs.get("clip_weight_2")
        switch_3 = kwargs.get("switch_3")
        lora_name_3 = kwargs.get("lora_name_3")
        model_weight_3 = kwargs.get("model_weight_3")
        clip_weight_3 = kwargs.get("clip_weight_3")
        lora_stack = kwargs.get("lora_stack")

        lora_list: list = []
        if lora_stack is not None:
            lora_list.extend([lora for lora in lora_stack if lora[0] != "None"])

        if lora_name_1 != "None" and switch_1 == "On":
            (lora_list.extend([(lora_name_1, model_weight_1, clip_weight_1)]),)  # type: ignore

        if lora_name_2 != "None" and switch_2 == "On":
            (lora_list.extend([(lora_name_2, model_weight_2, clip_weight_2)]),)  # type: ignore

        if lora_name_3 != "None" and switch_3 == "On":
            (lora_list.extend([(lora_name_3, model_weight_3, clip_weight_3)]),)  # type: ignore

        return (lora_list,)
