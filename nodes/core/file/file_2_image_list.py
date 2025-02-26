import torch
from signature_core.img.tensor_image import TensorImage

from ...categories import FILE_CAT


class File2ImageList:
    """Converts file references to a list of image tensors.

    Processes a list of file references, extracting and converting supported image files into
    ComfyUI-compatible tensor format.

    Args:
        files (list): List of file dictionaries with type and path information.

    Returns:
        tuple[list[torch.Tensor]]:
            - images: List of BWHC format tensors from valid image files

    Raises:
        ValueError: If input is not a list
        IOError: If image loading fails
        RuntimeError: If tensor conversion fails

    Notes:
        - Supports PNG, JPG, JPEG, TIFF, BMP formats
        - Skips non-image files
        - Maintains original image properties
        - Returns empty list if no valid images
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "files": ("FILE", {"default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = FILE_CAT
    CLASS_ID = "file_image_list"
    OUTPUT_IS_LIST = (True,)
    DESCRIPTION = "Converts file references to a list of image tensors. Processes multiple files, extracting supported image formats (PNG, JPG, JPEG, TIFF, BMP) into ComfyUI-compatible format."

    def execute(self, files: list[dict]) -> tuple[list[torch.Tensor]]:
        images_list = []
        for file in files:
            mimetype = file["type"]
            extension = file["name"].lower().split(".")[-1]
            possible_extensions = ["png", "jpg", "jpeg", "tiff", "tif", "bmp"]
            if mimetype.startswith("image") and extension in possible_extensions:
                images_list.append(TensorImage.from_local(file["name"]).get_BWHC())

        return (images_list,)
