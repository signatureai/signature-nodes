import json
import os
from typing import Optional

import comfy.model_management  # type: ignore
import folder_paths  # type: ignore
import torch
from neurochain.embeddings.builder import build_embedder_for_model_name
from neurochain.embeddings.models import MODEL_REPOSITORY
from signature_core.img.tensor_image import TensorImage

from ...categories import EMBEDDINGS_CAT

SIG_EMBEDDINGS_DIR = "sig_embeddings"


class GetEmbeddings:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (
                    [model["name"] for model in MODEL_REPOSITORY],
                    {"default": "resnet50"},
                ),
            },
            "optional": {
                "image": ("IMAGE",),
                "text": ("STRING",),
                "sig_additional_metadata": (
                    "STRING",
                    {
                        "default": json.dumps(
                            {
                                model["name"]: {
                                    "showText": model["supports_text"],
                                    "showImage": model["supports_image"],
                                }
                                for model in MODEL_REPOSITORY
                            }
                        ),
                    },
                ),
            },
        }

    RETURN_TYPES = ("LIST", "LIST")
    RETURN_NAMES = ("image_embeddings", "text_embeddings")
    FUNCTION = "process"
    CATEGORY = EMBEDDINGS_CAT
    OUTPUT_NODE = True

    def process(
        self,
        model: str,
        image: Optional[torch.Tensor] = None,
        text: Optional[str] = None,
    ):
        (output_image_embeddings, output_text_embeddings) = self._validate_model_and_inputs(model, image, text)

        embeddings_path = os.path.join(folder_paths.models_dir, SIG_EMBEDDINGS_DIR)
        if not os.path.exists(embeddings_path):
            os.makedirs(embeddings_path)

        text_embeddings = []
        image_embeddings = []

        device = comfy.model_management.get_torch_device()
        embedder = build_embedder_for_model_name(model_name=model, model_base_path=embeddings_path, device=device)
        model_data = [m for m in MODEL_REPOSITORY if m["name"] == model][0]
        if model_data["supports_image"] and model_data["supports_text"]:
            tensor_img = None
            if image is not None:
                tensor_img = TensorImage.from_BWHC(data=image)
            image_embeddings, text_embeddings = embedder.embed(image=tensor_img, text=text)
        elif model_data["supports_image"]:
            tensor_img = TensorImage.from_BWHC(data=image)  # type: ignore
            image_embeddings = embedder.embed(image=tensor_img)
        elif model_data["supports_text"]:
            text_embeddings = embedder.embed(text=text)

        if output_image_embeddings and not output_text_embeddings:
            return (image_embeddings,)
        if output_text_embeddings and not output_image_embeddings:
            return (text_embeddings,)
        return (image_embeddings, text_embeddings)

    def _validate_model_and_inputs(
        self, model: str, image: Optional[torch.Tensor], text: Optional[str]
    ) -> tuple[bool, bool]:
        model_map = {model["name"]: model for model in MODEL_REPOSITORY}
        if model not in model_map:
            raise ValueError(f"Invalid model: {model}")
        if model_map[model]["supports_text"] and not model_map[model]["supports_image"] and text is None:
            raise ValueError("Text is required for this model")
        if model_map[model]["supports_image"] and not model_map[model]["supports_text"] and image is None:
            raise ValueError("Image is required for this model")
        if text is None and image is None:
            raise ValueError("Either text or image or both must be provided")

        return (model_map[model]["supports_image"], model_map[model]["supports_text"])
