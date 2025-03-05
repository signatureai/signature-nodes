from typing import Optional

from neurochain.detectors.dino import DINOSimilarity
from signature_core.img.tensor_image import TensorImage
from torch import Tensor

from ...categories import LABS_CAT


class DINOHeatmap:
    """A ComfyUI node that generates similarity heatmaps using DINO Vision Transformer.

    This node takes an input image and a template image, optionally with a mask,
    and produces a heatmap showing regions similar to the template using DINO embeddings.
    """

    CLASS_ID = "dino_heatmap"
    CATEGORY = LABS_CAT
    DESCRIPTION = """Generates a similarity heatmap between two images using DINO Vision Transformer.

    This node helps you find regions in an image that are similar to a template image. It uses Facebook's DINOv2
    Vision Transformer model to analyze the images and create a heatmap highlighting matching areas.

    Inputs:
    - Image: The main image to analyze
    - Template: The reference image to search for
    - Mask (optional): A mask to focus the search on specific areas of the template. If provided, mask dimensions (H, W)
      should be equal to those of the template.

    Output:
    - A heatmap image where brighter areas indicate stronger similarity to the template

    When a mask is provided, the node will direct attention to specific regions of the template defined by the mask.
    If no mask is provided, the entire template will be considered for similarity matching.

    This is useful for:
    - Finding specific objects or patterns in images
    - Analyzing image composition and recurring elements
    - Visual pattern matching and comparison
    - Object localization without traditional object detection"""

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
        image = TensorImage.from_BWHC(image)
        template = TensorImage.from_BWHC(template)
        mask = TensorImage.from_BWHC(mask) if mask is not None else None

        model = DINOSimilarity()
        output = model.predict(image, template, mask)

        output = TensorImage(output).get_BWHC()
        return (output,)
