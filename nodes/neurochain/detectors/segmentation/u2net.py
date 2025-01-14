from pathlib import Path

import torch
from neurochain.detectors.segmentation.u2net import U2Net

from ....categories import SEGMENTATION_CAT


class U2NetNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "clearml_model_id": ("STRING", {"default": "43248a75117d4f4db2d9187fea288eff"}),
                "use_binary_mask": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process"
    CATEGORY = SEGMENTATION_CAT

    def process(self, image: torch.Tensor, clearml_model_id: str, use_binary_mask: bool):
        root_dir = Path(__file__).parent.parent.parent
        checkpoint_dir = root_dir / "models" / "checkpoints"
        model = U2Net(model_id=clearml_model_id, checkpoint_dir=checkpoint_dir, use_binary_mask=use_binary_mask)
        output = model.predict(image)
        return (output,)
