import comfy.model_management  # type: ignore
import torch
from neurochain.embeddings.resnet50 import Resnet50
from signature_core.img.tensor_image import TensorImage

from ...categories import EMBEDDINGS_CAT


class GetEmbeddings:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("embeddings",)
    FUNCTION = "process"
    CATEGORY = EMBEDDINGS_CAT
    OUTPUT_NODE = True

    def process(self, image: torch.Tensor):
        device = comfy.model_management.get_torch_device()

        tensor_img = TensorImage.from_BWHC(data=image)

        resnet50 = Resnet50(str(device) if device is not None else None)
        embeddings = resnet50.embed(tensor_img)

        return (embeddings,)
