import cv2 as cv
import torch
from torchvision import ops
from torchvision.transforms import v2

from .categories import NAME


class OTSUNode:
    """A node that performs Otsu's thresholding on an input image.

    This node implements Otsu's method, which automatically determines an optimal threshold
    value by minimizing intra-class intensity variance. It converts the input image to
    grayscale and applies binary thresholding using the computed optimal threshold.

    Args:
        image (torch.Tensor): The input image tensor to threshold.
                            Expected shape: (B, H, W, C)

    Returns:
        tuple[float, torch.Tensor]: A tuple containing:
            - The computed Otsu threshold value
            - The thresholded binary image as a tensor with shape (B, H, W, C)

    Notes:
        - The input image is automatically converted to grayscale before thresholding
        - The output binary image contains values of 0 and 255
        - The threshold computation is performed using OpenCV's implementation
    """
    CATEGORY = f"{NAME}/🧪 Experimental"

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
