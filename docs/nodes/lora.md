# Lora Nodes

## ApplyLoraStack

Applies multiple LoRA models sequentially to a base model and CLIP in ComfyUI.

This node takes a base model, CLIP, and a stack of LoRA models as input. It applies each LoRA
in the stack sequentially using specified weights for both model and CLIP components.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | model | `MODEL` |  |  |
| required | clip | `CLIP` |  |  |
| required | lora_stack | `LORA_STACK` |  |  |

### Returns

| Name | Type |
|------|------|
| model | `MODEL` |
| clip | `CLIP` |


??? note "Source code"

    ```python
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

        def execute(
            self,
            **kwargs,
        ):
            model = kwargs.get("model")
            clip = kwargs.get("clip")
            lora_stack = kwargs.get("lora_stack")
            loras = []
            if lora_stack is None:
                return (
                    model,
                    clip,
                )

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


    ```

## LoraStacker

Manages multiple LoRA models with configurable weights and modes.

This node provides an interface for stacking multiple LoRA models with independent
weight controls and two operating modes for simple or advanced weight management.

### Returns

| Name | Type |
|------|------|
| lora_stack | `LORA_STACK` |


??? note "Source code"

    ```python
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
                        f"weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                        f"model_weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                        f"clip_weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    }
                )

            return inputs

        RETURN_TYPES = ("LORA_STACK",)
        RETURN_NAMES = ("lora_stack",)
        FUNCTION = "execute"
        CATEGORY = LABS_CAT
        CLASS_ID = "lora_stacker"

        def execute(self, **kwargs):
            num_slots = int(kwargs.get("num_slots", 3))
            mode = kwargs.get("mode", "Simple")
            lora_stack = kwargs.get("lora_stack")

            lora_list: list = []
            if lora_stack is not None:
                lora_list.extend([l for l in lora_stack if l[0] is not None and l[0] != ""])

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


    ```

## LoraStack

Creates a configurable stack of up to 3 LoRA models with adjustable weights.

Provides a user interface to enable/disable and configure up to three LoRA models with independent
weights for both model and CLIP components. Can extend an existing LORA_STACK.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | switch_1 | `LIST` |  |  |
| required | lora_name_1 | `loras` |  |  |
| required | model_weight_1 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| required | clip_weight_1 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| required | switch_2 | `LIST` |  |  |
| required | lora_name_2 | `loras` |  |  |
| required | model_weight_2 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| required | clip_weight_2 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| required | switch_3 | `LIST` |  |  |
| required | lora_name_3 | `loras` |  |  |
| required | model_weight_3 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| required | clip_weight_3 | `FLOAT` | 1.0 | max=10.0, step=0.01 |
| optional | lora_stack | `LORA_STACK` |  |  |

### Returns

| Name | Type |
|------|------|
| lora_stack | `LORA_STACK` |


??? note "Source code"

    ```python
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
                        f"weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                        f"model_weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                        f"clip_weight_{i}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    }
                )

            return inputs

        RETURN_TYPES = ("LORA_STACK",)
        RETURN_NAMES = ("lora_stack",)
        FUNCTION = "execute"
        CATEGORY = LABS_CAT
        CLASS_ID = "lora_stacker"

        def execute(self, **kwargs):
            num_slots = int(kwargs.get("num_slots", 3))
            mode = kwargs.get("mode", "Simple")
            lora_stack = kwargs.get("lora_stack")

            lora_list: list = []
            if lora_stack is not None:
                lora_list.extend([l for l in lora_stack if l[0] is not None and l[0] != ""])

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
                    "model_weight_1": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    "clip_weight_1": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    "switch_2": (["Off", "On"],),
                    "lora_name_2": (loras,),
                    "model_weight_2": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    "clip_weight_2": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    "switch_3": (["Off", "On"],),
                    "lora_name_3": (loras,),
                    "model_weight_3": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                    "clip_weight_3": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
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
                lora_list.extend([l for l in lora_stack if l[0] != "None"])

            if lora_name_1 != "None" and switch_1 == "On":
                (lora_list.extend([(lora_name_1, model_weight_1, clip_weight_1)]),)  # type: ignore

            if lora_name_2 != "None" and switch_2 == "On":
                (lora_list.extend([(lora_name_2, model_weight_2, clip_weight_2)]),)  # type: ignore

            if lora_name_3 != "None" and switch_3 == "On":
                (lora_list.extend([(lora_name_3, model_weight_3, clip_weight_3)]),)  # type: ignore

            return (lora_list,)


    ```

## Dict2LoraStack

Converts a list of LoRA configuration dictionaries into a LORA_STACK format.

Transforms a list of dictionaries containing LoRA configurations into the tuple format required
for LORA_STACK operations. Can optionally extend an existing stack.

### Returns

| Name | Type |
|------|------|
| lora_stack | `LORA_STACK` |


??? note "Source code"

    ```python
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

            inputs["optional"] = {"lora_stack": ("LORA_STACK",)}
            return inputs

        RETURN_TYPES = ("LORA_STACK",)
        RETURN_NAMES = ("lora_stack",)
        FUNCTION = "execute"
        CATEGORY = LORA_CAT
        CLASS_ID = "dict_to_lora_stack"

        def execute(self, **kwargs):
            lora_dicts = kwargs.get("lora_dicts")
            if not isinstance(lora_dicts, list):
                raise ValueError("Lora dicts must be a list")
            lora_stack = kwargs.get("lora_stack")
            loras = [None for _ in lora_dicts]

            for idx, lora_dict in enumerate(lora_dicts):
                loras[idx] = (lora_dict["lora_name"], lora_dict["lora_weight"], lora_dict["lora_weight"])  # type: ignore

            # If lora_stack is not None, extend the loras list with lora_stack
            if lora_stack is not None:
                loras.extend([l for l in lora_stack if l[0] != "None"])

            return (loras,)


    ```

## SaveLoraCaptions

Saves images and captions in a format suitable for LoRA training.

Creates a structured dataset directory containing images and their corresponding caption files,
with support for multiple captions and optional text modifications.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | dataset_name | `STRING` |  |  |
| required | repeats | `INT` | 5 | min=1 |
| required | images | `IMAGE` |  |  |
| required | labels | `STRING` |  | forceInput=True |
| optional | prefix | `STRING` |  |  |
| optional | suffix | `STRING` |  |  |

### Returns

| Name | Type |
|------|------|
| string | `STRING` |


??? note "Source code"

    ```python
    class SaveLoraCaptions:
        """Saves images and captions in a format suitable for LoRA training.

        Creates a structured dataset directory containing images and their corresponding caption files,
        with support for multiple captions and optional text modifications.

        Args:
            dataset_name (str): Name for the dataset folder
            repeats (int): Number of times to repeat the dataset (min: 1)
            images (IMAGE): Tensor containing the images to save
            labels (str): Caption text, multiple captions separated by newlines
            prefix (str, optional): Text to add before each caption
            suffix (str, optional): Text to add after each caption

        Returns:
            tuple:
                - str: Path to the created dataset folder

        Raises:
            ValueError: If any input parameters are of incorrect type

        Notes:
            - Creates folder structure: comfy/loras_datasets/dataset_name_uuid/repeats_dataset_name/
            - Saves images as PNG files with corresponding .txt caption files
            - Supports multiple captions via newline separation
            - Includes UUID in folder name for uniqueness
            - Creates parent directories if they don't exist
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "dataset_name": ("STRING", {"default": ""}),
                    "repeats": ("INT", {"default": 5, "min": 1}),
                    "images": ("IMAGE",),
                    "labels": ("STRING", {"forceInput": True}),
                },
                "optional": {
                    "prefix": ("STRING", {"default": ""}),
                    "suffix": ("STRING", {"default": ""}),
                },
            }

        RETURN_TYPES = ("STRING",)
        RETURN_NAMES = ("folder_path",)
        OUTPUT_NODE = True
        FUNCTION = "execute"
        CATEGORY = LORA_CAT

        def execute(
            self,
            **kwargs,
        ):
            dataset_name = kwargs.get("dataset_name")
            if not isinstance(dataset_name, str):
                raise ValueError("Dataset name must be a string")
            repeats = kwargs.get("repeats")
            if not isinstance(repeats, int):
                raise ValueError("Repeats must be an integer")
            images = kwargs.get("images")
            if not isinstance(images, torch.Tensor):
                raise ValueError("Images must be a torch.Tensor")
            labels = kwargs.get("labels")
            if not isinstance(labels, str):
                raise ValueError("Labels must be a string")
            prefix = kwargs.get("prefix")
            if not isinstance(prefix, str):
                raise ValueError("Prefix must be a string")
            suffix = kwargs.get("suffix")
            if not isinstance(suffix, str):
                raise ValueError("Suffix must be a string")

            labels_list = labels.split("\n") if "\n" in labels else [labels]

            root_folder = os.path.join(BASE_COMFY_DIR, "loras_datasets")
            if not os.path.exists(root_folder):
                os.mkdir(root_folder)

            uuid = uuid7str()
            dataset_folder = os.path.join(root_folder, f"{dataset_name}_{uuid}")
            if not os.path.exists(dataset_folder):
                os.mkdir(dataset_folder)
            images_folder = os.path.join(dataset_folder, f"{repeats}_{dataset_name}")
            if not os.path.exists(images_folder):
                os.mkdir(images_folder)

            tensor_images = TensorImage.from_BWHC(images)
            for i, img in enumerate(tensor_images):
                # timestamp to be added to the image name

                TensorImage(img).save(os.path.join(images_folder, f"{dataset_name}_{i}.png"))
                # write txt label with the same name of the image
                with open(os.path.join(images_folder, f"{dataset_name}_{i}.txt"), "w") as f:
                    label = prefix + labels_list[i % len(labels_list)] + suffix
                    f.write(label)

            return (dataset_folder,)

    ```
