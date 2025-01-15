from pathlib import Path

import folder_paths  # type: ignore
import torch
from neurochain.detectors.segmentation.u2net import U2Net

from ....categories import SEGMENTATION_CAT


class U2NetNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "clearml_model_id": ("STRING", {"default": "fefce5f3d54a479fa02c84f6fdf3b8a2"}),
            },
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "process"
    CATEGORY = SEGMENTATION_CAT

    def process(self, image: torch.Tensor, clearml_model_id: str):
        checkpoint_dir = Path(folder_paths.models_dir) / "checkpoints"
        model = U2Net(model_id=clearml_model_id, checkpoint_dir=checkpoint_dir)
        output = model.predict(image)
        return (output,)

