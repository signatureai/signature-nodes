import os
from typing import Optional

import torch
from signature_core.img.tensor_image import TensorImage
from uuid_extensions import uuid7str

from ...categories import LORA_CAT
from ...shared import BASE_COMFY_DIR


# * Move this to signature dojo
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
