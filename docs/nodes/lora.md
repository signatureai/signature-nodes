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
        DESCRIPTION = """
        Applies multiple LoRA models sequentially to a base model and CLIP.
        Processes each LoRA in the stack with specified weights for both model and CLIP components.
        Useful for combining multiple style or concept adaptations in a single workflow.
        """

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
            return inputs

        RETURN_TYPES = ("LORA_STACK",)
        FUNCTION = "execute"
        CATEGORY = LORA_CAT
        CLASS_ID = "dict_to_lora_stack"
        DESCRIPTION = """
        Converts a list of LoRA configuration dictionaries into a LORA_STACK format.
        Transforms dictionaries with lora_name and lora_weight into tuples for LORA_STACK operations.
        Can optionally extend an existing stack.
        """

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
        DESCRIPTION = """
        Creates a configurable stack of up to 3 LoRA models with adjustable weights.
        Provides controls to enable/disable and configure each LoRA with independent weights for model and CLIP components.
        Can extend an existing stack.
        """

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
    ```

## BuildLoraDataset

Saves images and captions in a format suitable for LoRA training.

Creates a structured dataset directory containing images and their corresponding caption files,
with support for multiple captions and optional text modifications.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | images | `IMAGE` |  |  |
| required | labels | `LIST` |  | forceInput=True |
| required | dataset_name | `STRING` | dataset |  |
| required | repeats | `INT` | 5 | min=1 |
| required | training_backend | `LIST` |  |  |
| optional | prefix | `STRING` |  |  |
| optional | suffix | `STRING` |  |  |

### Returns

| Name | Type |
|------|------|
| string | `STRING` |


??? note "Source code"

    ```python
    class BuildLoraDataset:
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
                    "images": ("IMAGE",),
                    "labels": ("LIST", {"forceInput": True}),
                    "dataset_name": ("STRING", {"default": "dataset"}),
                    "repeats": ("INT", {"default": 5, "min": 1}),
                    "training_backend": (["ai-toolkit", "simpletuner"],),
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
        DESCRIPTION = """
        Saves images and captions in a format suitable for LoRA training.
        Creates a structured dataset directory with images and corresponding caption files.
        Supports multiple captions, repeats, and optional text modifications with prefix/suffix.
        """

        # Add a class variable to track the counter across function calls
        _counter = 0

        def execute(
            self,
            images: torch.Tensor,
            labels: list[str],
            dataset_name: str = "dataset",
            repeats: int = 5,
            prefix: Optional[str] = "",
            suffix: Optional[str] = "",
            training_backend: str = "ai-toolkit",
        ) -> tuple[str]:
            print("dataset_name", dataset_name, type(dataset_name))
            if len(dataset_name) == 0:
                dataset_name = "dataset"
            root_folder = os.path.join(BASE_COMFY_DIR, "loras_datasets")
            if not os.path.exists(root_folder):
                os.mkdir(root_folder)

            dataset_folder = None
            if training_backend == "ai-toolkit":
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
                        label = prefix + labels[self._counter % len(labels)] + suffix  # type: ignore
                        f.write(label)
                    self._counter += 1
            elif training_backend == "simpletuner":
                dataset_folder = os.path.join(root_folder, dataset_name)
                if not os.path.exists(dataset_folder):
                    os.mkdir(dataset_folder)

                tensor_images = TensorImage.from_BWHC(images)
                for i, img in enumerate(tensor_images):
                    uuid = uuid7str()
                    # Save images directly to the dataset folder
                    TensorImage(img).save(os.path.join(dataset_folder, f"{dataset_name}_{uuid}.png"))

                    # Write txt label with the same name of the image
                    with open(os.path.join(dataset_folder, f"{dataset_name}_{uuid}.txt"), "w") as f:
                        # Use modulo to cycle through labels if needed
                        label = str(prefix) + labels[self._counter % len(labels)] + str(suffix)
                        f.write(label)

                    self._counter += 1

            return (str(dataset_folder),)

    ```
