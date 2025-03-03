import os
from typing import Optional

import torch
from signature_core.img.tensor_image import TensorImage
from uuid_extensions import uuid7str

from ...categories import LORA_CAT
from ...shared import BASE_COMFY_DIR


# * Move this to signature dojo
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
                "images": ("IMAGE",),
                "labels": ("STRING", {"forceInput": True}),
                "dataset_name": ("STRING", {"default": ""}),
                "repeats": ("INT", {"default": 5, "min": 1}),
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
    DESCRIPTION = "Saves images and captions in a format suitable for LoRA training. Creates a structured dataset directory with images and corresponding caption files. Supports multiple captions, repeats, and optional text modifications with prefix/suffix."

    def execute(
        self,
        images: torch.Tensor,
        labels: str,
        dataset_name: str = "",
        repeats: int = 5,
        prefix: Optional[str] = "",
        suffix: Optional[str] = "",
    ):
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
                label = prefix + labels_list[i % len(labels_list)] + suffix  # type: ignore
                f.write(label)

        return (dataset_folder,)
