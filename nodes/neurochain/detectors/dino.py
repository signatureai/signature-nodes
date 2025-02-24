from typing import Optional

from neurochain.detectors.dino import DINOSimilarity
from torch import Tensor

from ...categories import LABS_CAT


class DINOHeatmap:
    """A ComfyUI node that generates similarity heatmaps using DINO Vision Transformer.

    This node takes an input image and a template image, optionally with a mask,
    and produces a heatmap showing regions similar to the template using DINO embeddings.
    """
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
        model = DINOSimilarity()
        output = model.predict(image, template, mask)
        return (output,)
