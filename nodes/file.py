import json
import os

import torch
from signature_core.img.tensor_image import TensorImage

from .categories import FILE_CAT
from .shared import BASE_COMFY_DIR


def image_array_to_tensor(x: TensorImage):
    image = x.get_BWHC()
    mask = torch.ones((x.shape[0], x.shape[2], x.shape[3], 1), dtype=torch.float32)

    if x.shape[-1] == 4:
        mask = image[:, :, :, -1]

    return (
        image,
        mask,
    )


class ImageFromWeb:
    """Fetches and converts web images to ComfyUI-compatible tensors.

    Downloads an image from a URL and processes it into ComfyUI's expected tensor format. Handles both RGB
    and RGBA images with automatic mask generation for transparency.

    Args:
        url (str): Direct URL to the image file (PNG, JPG, JPEG, WebP).

    Returns:
        tuple[torch.Tensor, torch.Tensor]:
            - image: BWHC format tensor, normalized to [0,1] range
            - mask: BWHC format tensor for transparency/alpha channel

    Raises:
        ValueError: If URL is invalid, inaccessible, or not a string
        HTTPError: If image download fails
        IOError: If image format is unsupported

    Notes:
        - Automatically converts images to float32 format
        - RGB images get a mask of ones
        - RGBA images use alpha channel as mask
        - Supports standard web image formats
        - Image dimensions are preserved
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {"required": {"url": ("STRING", {"default": "URL HERE"})}}

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "execute"
    CATEGORY = FILE_CAT

    def execute(self, **kwargs):
        url = kwargs.get("url")
        if not isinstance(url, str):
            raise ValueError("URL must be a string")
        img_arr = TensorImage.from_web(url)
        return image_array_to_tensor(img_arr)


class ImageFromBase64:
    """Converts base64 image strings to ComfyUI-compatible tensors.

    Processes base64-encoded image data into tensor format suitable for ComfyUI operations. Handles
    both RGB and RGBA images with proper mask generation.

    Args:
        base64 (str): Raw base64-encoded image string without data URL prefix.

    Returns:
        tuple[torch.Tensor, torch.Tensor]:
            - image: BWHC format tensor, normalized to [0,1] range
            - mask: BWHC format tensor for transparency/alpha channel

    Raises:
        ValueError: If base64 string is invalid or not a string
        IOError: If decoded image format is unsupported
        binascii.Error: If base64 decoding fails

    Notes:
        - Converts decoded images to float32 format
        - RGB images get a mask of ones
        - RGBA images use alpha channel as mask
        - Supports common image formats (PNG, JPG, JPEG)
        - Original image dimensions are preserved
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {"required": {"base64": ("STRING", {"default": "BASE64 HERE"})}}

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "execute"
    CATEGORY = FILE_CAT

    def execute(self, **kwargs):
        base64 = kwargs.get("base64")
        if not isinstance(base64, str):
            raise ValueError("Base64 must be a string")
        img_arr = TensorImage.from_base64(base64)
        return image_array_to_tensor(img_arr)


class Base64FromImage:
    """Converts ComfyUI image tensors to base64-encoded strings.

    Transforms image tensors from ComfyUI's format into base64-encoded strings, suitable for web
    transmission or storage in text format.

    Args:
        image (torch.Tensor): BWHC format tensor with values in [0,1] range.

    Returns:
        tuple[str]:
            - base64_str: PNG-encoded image as base64 string without data URL prefix

    Raises:
        ValueError: If input is not a tensor or has invalid format
        RuntimeError: If tensor conversion or encoding fails

    Notes:
        - Output is always PNG encoded
        - Preserves alpha channel if present
        - No data URL prefix in output
        - Maintains original image quality
        - Suitable for web APIs and storage
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {"required": {"image": ("IMAGE",)}}

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = FILE_CAT
    OUTPUT_NODE = True

    def execute(self, **kwargs):
        image = kwargs.get("image")
        if not isinstance(image, torch.Tensor):
            raise ValueError("Image must be a torch.Tensor")
        images = TensorImage.from_BWHC(image)
        output = images.get_base64()
        return (output,)


class FileLoader:
    """Processes string input into ComfyUI-compatible file data.

    Converts JSON-formatted string data into file references with proper paths for ComfyUI processing.
    Handles both single files and multiple files separated by '&&'.

    Args:
        value (str): JSON-formatted string containing file data.

    Returns:
        tuple[list]:
            - files: List of dictionaries with file data and updated paths

    Raises:
        ValueError: If input is not a string
        json.JSONDecodeError: If JSON parsing fails
        KeyError: If required file data fields are missing

    Notes:
        - Automatically prepends ComfyUI input folder path
        - Supports multiple files via '&&' separator
        - Preserves original file metadata
        - Updates file paths for ComfyUI compatibility
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("FILE",)
    FUNCTION = "execute"
    CATEGORY = FILE_CAT

    def execute(self, **kwargs):
        value = kwargs.get("value")
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        data = value.split("&&") if "&&" in value else [value]
        input_folder = os.path.join(BASE_COMFY_DIR, "input")
        for i, _ in enumerate(data):
            json_str = data[i]
            data[i] = json.loads(json_str)
            item = data[i]
            if isinstance(item, dict):
                name = item.get("name", None)
                if name is None:
                    continue
                item["name"] = os.path.join(input_folder, name)
                data[i] = item

        return (data,)


class FolderLoader:
    """Processes folder paths into ComfyUI-compatible file data.

    Converts folder path information into properly formatted file references for ComfyUI processing.
    Supports both single and multiple folder paths.

    Args:
        value (str): JSON-formatted string containing folder path data.

    Returns:
        tuple[list]:
            - files: List of dictionaries with file data and updated paths

    Raises:
        ValueError: If input is not a string
        json.JSONDecodeError: If JSON parsing fails
        KeyError: If required folder data fields are missing

    Notes:
        - Automatically prepends ComfyUI input folder path
        - Supports multiple folders via '&&' separator
        - Maintains folder structure information
        - Updates all paths for ComfyUI compatibility
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("FILE",)
    FUNCTION = "execute"
    CATEGORY = FILE_CAT

    def execute(self, **kwargs):
        value = kwargs.get("value")
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        data = value.split("&&") if "&&" in value else [value]
        input_folder = os.path.join(BASE_COMFY_DIR, "input")
        for i, _ in enumerate(data):
            json_str = data[i]
            data[i] = json.loads(json_str)
            item = data[i]
            if isinstance(item, dict):
                name = item.get("name", None)
                if name is None:
                    continue
                item["name"] = os.path.join(input_folder, name)
                data[i] = item
        return (data,)


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

    def execute(self, **kwargs):
        files = kwargs.get("files")
        if not isinstance(files, list):
            raise ValueError("Files must be a list")
        images_list = []
        for file in files:
            mimetype = file["type"]
            extension = file["name"].lower().split(".")[-1]
            possible_extensions = ["png", "jpg", "jpeg", "tiff", "tif", "bmp"]
            if mimetype.startswith("image") and extension in possible_extensions:
                images_list.append(TensorImage.from_local(file["name"]).get_BWHC())

        return (images_list,)


class File2List:
    """Converts file input to a standardized list format.

    Processes file input data into a consistent list format for further ComfyUI operations.

    Args:
        files (list): List of file dictionaries.

    Returns:
        tuple[list]:
            - files: Processed list of file data

    Raises:
        ValueError: If input is not a list

    Notes:
        - Preserves original file metadata
        - Maintains file order
        - No file validation performed
        - Suitable for further processing
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "files": ("FILE", {"default": ""}),
            },
        }

    RETURN_TYPES = ("LIST",)
    FUNCTION = "execute"
    CLASS_ID = "file_list"
    CATEGORY = FILE_CAT

    def execute(self, **kwargs):
        files = kwargs.get("files")
        if not isinstance(files, list):
            raise ValueError("Files must be a list")
        return (files,)


class Rotate:
    """Rotates an image and mask by a specified angle.

    This node provides functionality to rotate images and masks while optionally adjusting the output
    size to fit the entire rotated content.

    Args:
        image (torch.Tensor, optional): Input image in BWHC format
        mask (torch.Tensor, optional): Input mask in BWHC format
        angle (float): Rotation angle in degrees (0-360)
        zoom_to_fit (bool): Whether to zoom to fit rotated content (default: False)

    Returns:
        tuple[torch.Tensor, torch.Tensor]: Tuple containing:
            - Rotated image in BWHC format
            - Rotated mask in BWHC format

    Notes:
        - At least one of image or mask must be provided
        - Rotation is performed counterclockwise
        - When zoom_to_fit is False, corners may be clipped
        - When zoom_to_fit is True, output may be larger
        - Empty areas after rotation are filled with black
        - Maintains aspect ratio of input
    """


class MaskGaussianBlur:
    """Applies Gaussian blur to a mask.

    This node performs Gaussian blur on mask inputs with configurable radius, sigma and iteration
    parameters. Useful for softening mask edges or creating smooth transitions.

    Args:
        image (torch.Tensor): Input mask in BWHC format
        radius (int): Blur radius in pixels. Default: 13
            Larger values create wider blur effects
        sigma (float): Blur strength/standard deviation. Default: 10.5
            Controls the falloff of the blur effect
        iterations (int): Number of blur passes to apply. Default: 1
            Multiple passes can create stronger blur effects
        only_outline (bool): Whether to blur only the outline. Default: False
            When True, preserves solid areas and only blurs edges

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing:
            - Blurred mask in BWHC format

    Notes:
        - Input should be a single-channel mask
        - Output maintains the same dimensions as input
        - Multiple iterations can create smoother results
        - Larger radius and sigma values produce stronger blur
        - Edge-only mode is useful for creating soft borders
    """
