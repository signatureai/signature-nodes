import cv2 as cv
import torch
from torchvision import ops
from torchvision.transforms import v2


class OTSUNode:
    # TODO: Add node documentation
    CATEGORY = "example"  # TODO: Change this to the correct category

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("FLOAT", "IMAGE")
    FUNCTION = "execute"

    def execute(self, image: torch.Tensor) -> tuple[float, torch.Tensor]:
        img_transformed = v2.Compose(
            [
                ops.Permute(dims=(0, 3, 2, 1)),
                v2.Grayscale(),
                v2.ToDtype(torch.uint8, scale=True),
            ]
        )(image)
        img_np = img_transformed.squeeze().cpu().numpy()

        thresh, out = cv.threshold(img_np, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

        out_torch = torch.from_numpy(out).to(image.device).unsqueeze(0).unsqueeze(0)
        out_transformed = v2.Compose([v2.RGB(), ops.Permute(dims=(0, 3, 2, 1))])(out_torch)
        return (thresh, out_transformed)
