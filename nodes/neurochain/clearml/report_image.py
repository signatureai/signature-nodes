import torch
from clearml import Task
from signature_core.img.tensor_image import TensorImage

from ...categories import CLEARML_CAT


class ReportImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "task": ("CLEARML_TASK", {}),
                "image": ("IMAGE",),
                "collection_name": ("STRING", {"default": ""}),
                "image_name": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("CLEARML_TASK",)
    RETURN_NAMES = ("clearml_task",)
    FUNCTION = "process"
    CATEGORY = CLEARML_CAT
    OUTPUT_NODE = True

    def process(self, task: Task, image: torch.Tensor, collection_name: str = "Samples", image_name: str = "image"):
        tensor_img = TensorImage.from_BWHC(data=image)
        np_img = tensor_img.get_numpy_image()

        task.get_logger().report_image(collection_name, f"Image {image_name}", iteration=0, image=np_img)
        return (task,)
