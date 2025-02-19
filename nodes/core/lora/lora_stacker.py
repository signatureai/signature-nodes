import folder_paths  # type: ignore

from ...categories import LABS_CAT


class LoraStacker:
    """Manages multiple LoRA models with configurable weights and modes.

    This node provides an interface for stacking multiple LoRA models with independent
    weight controls and two operating modes for simple or advanced weight management.

    Args:
        num_slots (str): Number of LoRA slots to enable (1-10)
        mode (str): Weight control mode:
            - "Simple": Single weight per LoRA
            - "Advanced": Separate model and CLIP weights
        switch_1..10 (str): "On"/"Off" toggle for each LoRA slot
        lora_name_1..10 (str): Name of LoRA model for each slot
        weight_1..10 (float): Weight value for simple mode (-10.0 to 10.0)
        model_weight_1..10 (float): Model weight for advanced mode (-10.0 to 10.0)
        clip_weight_1..10 (float): CLIP weight for advanced mode (-10.0 to 10.0)
        lora_stack (LORA_STACK, optional): Existing stack to extend

    Returns:
        tuple[LORA_STACK]: Single-element tuple containing list of configured LoRAs

    Notes:
        - Each slot can be independently enabled/disabled
        - Simple mode uses same weight for model and CLIP
        - Advanced mode allows separate model and CLIP weights
        - Weights can be negative for inverse effects
        - Can extend existing LORA_STACK
        - Disabled or empty slots are skipped
    """

    @classmethod
    def INPUT_TYPES(cls):
        loras = ["None"] + folder_paths.get_filename_list("loras")

        inputs = {
            "required": {
                "num_slots": ([str(i) for i in range(1, 11)], {"default": "1"}),
                "mode": (["Simple", "Advanced"],),
            },
            "optional": {"lora_stack": ("LORA_STACK",)},
        }

        for i in range(1, 11):
            inputs["optional"].update(
                {
                    f"switch_{i}": (["On", "Off"],),
                    f"lora_name_{i}": (loras,),
                    f"weight_{i}": (
                        "FLOAT",
                        {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                    ),
                    f"model_weight_{i}": (
                        "FLOAT",
                        {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                    ),
                    f"clip_weight_{i}": (
                        "FLOAT",
                        {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01},
                    ),
                }
            )

        return inputs

    RETURN_TYPES = ("LORA_STACK",)
    RETURN_NAMES = ("lora_stack",)
    FUNCTION = "execute"
    CATEGORY = LABS_CAT
    CLASS_ID = "lora_stacker"

    def execute(self, **kwargs):
        num_slots = int(kwargs.get("num_slots", 1))
        mode = kwargs.get("mode", "Simple")
        lora_stack = kwargs.get("lora_stack")

        lora_list: list = []
        if lora_stack is not None:
            lora_list.extend([lora for lora in lora_stack if lora[0] is not None and lora[0] != ""])

        for i in range(1, num_slots + 1):
            switch = kwargs.get(f"switch_{i}")
            lora_name = kwargs.get(f"lora_name_{i}") or "None"

            if lora_name is not None and lora_name != "None" and switch == "On":
                if mode == "Simple":
                    weight = float(kwargs.get(f"weight_{i}") or 1.0)
                    lora_list.extend([(lora_name, weight, weight)])
                else:
                    model_weight = float(kwargs.get(f"model_weight_{i}") or 1.0)
                    clip_weight = float(kwargs.get(f"clip_weight_{i}") or 1.0)
                    lora_list.extend([(lora_name, model_weight, clip_weight)])

        return (lora_list,)
