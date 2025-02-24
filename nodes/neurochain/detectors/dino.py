from pathlib import Path
from typing import Optional

from neurochain.detectors.dino import DINOSimilarity
from torch import Tensor

from ......folder_paths import models_dir
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

    def execute(self, image: Tensor, template: Tensor, mask: Optional[Tensor] = None) -> tuple[Tensor,]:
        checkpoint_dir = Path(models_dir) / "checkpoints"  # TODO: Decide on a directory for models
        model = DINOSimilarity(checkpoint_dir=checkpoint_dir)
        output = model.predict(image, template, mask)
        return (output,)
