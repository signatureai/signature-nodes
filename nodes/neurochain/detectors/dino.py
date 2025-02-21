from typing import Optional
from pathlib import Path
import torch
from torch import Tensor

import folder_paths
from ...categories import LABS_CAT


class DINOHeatmap:
    CLASS_ID = "dino_heatmap"
    CATEGORY = LABS_CAT

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "template": ("IMAGE",),
            },
            "optional": {
                "mask": ("MASK",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    def execute(self, image: Tensor, template: Tensor, mask: Optional[Tensor] = None) -> Tensor:
        checkpoint_dir = Path(folder_paths.models_dir) / "checkpoints"  # TODO: Decide on a directory for models
        return (image,)
