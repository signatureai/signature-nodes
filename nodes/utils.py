import ast
import time
from typing import Any

import torch
from signature_core.functional.color import (
    grayscale_to_rgb,
    rgb_to_grayscale,
    rgb_to_hls,
    rgb_to_hsv,
    rgba_to_rgb,
)
from signature_core.img.tensor_image import TensorImage

from .categories import UTILS_CAT
from .shared import any_type, clean_memory


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


class Any2String:
    """Converts any input value to its string representation.

    This utility node provides a simple way to convert any input value into a string format using
    Python's built-in str() function. Useful for debugging, logging, or text-based operations.

    Args:
        value (Any): The input value to be converted to a string.

    Returns:
        tuple[str]: A single-element tuple containing the string representation of the input value.

    Notes:
        - The conversion is done using Python's native str() function
        - All Python types are supported as they all implement __str__
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": (any_type,),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    CLASS_ID = "any_string"
    DESCRIPTION = """
    Converts any input value to its string representation.
    Converts any input value into a string format using Python's built-in str() function.
    Useful for debugging, logging, or text-based operations.
    """

    def execute(self, value: Any) -> tuple[str]:
        return (str(value),)


class String2Any:
    """Safely converts a string representation to its Python object.

    Uses Python's ast.literal_eval for secure string evaluation, which only allows
    literal expressions (strings, numbers, tuples, lists, dicts, booleans, None).

    Args:
        string (str): String representation of a Python literal.

    Returns:
        tuple[Any]: A single-element tuple containing the evaluated Python object.

    Notes:
        - Only evaluates literal expressions, preventing code execution
        - Supports: strings, numbers, tuples, lists, dicts, booleans, None
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "string": ("STRING",),
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("value",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    DESCRIPTION = """
    Safely converts a string representation to its Python object.
    Uses Python's ast.literal_eval for secure string evaluation,
    which only allows literal expressions (strings, numbers, tuples, lists, dicts, booleans, None).
    Useful for converting string representations of Python objects back to their original Python objects.
    """

    def execute(self, string: str) -> tuple[Any]:
        try:
            return (ast.literal_eval(string),)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Invalid literal expression: {str(e)}")


class Any2Int:
    """Converts any input value to its int representation.

    This utility node provides a simple way to convert any input value into a int format using
    Python's built-in int() function. Useful for debugging, logging, or text-based operations.

    Args:
        value (Any): The input value to be converted to a int.

    Returns:
        tuple[int]: A single-element tuple containing the int representation of the input value.

    Notes:
        - The conversion is done using Python's native int() function
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": (any_type,),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    DESCRIPTION = """
    Converts any input value to its int representation.
    Converts any input value into a int format using Python's built-in int() function.
    Useful for debugging, logging, or text-based operations.
    """

    def execute(self, value: Any) -> tuple[int]:
        return (int(value),)


class Any2Float:
    """Converts any input value to its float representation.

    This utility node provides a simple way to convert any input value into a float format using
    Python's built-in float() function. Useful for debugging, logging, or text-based operations.

    Args:
        value (Any): The input value to be converted to a float.

    Returns:
        tuple[float]: A single-element tuple containing the float representation of the input value.

    Notes:
        - The conversion is done using Python's native float() function
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": (any_type,),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    DESCRIPTION = """
    Converts any input value to its float representation.
    Converts any input value into a float format using Python's built-in float() function.
    Useful for debugging, logging, or text-based operations.
    """

    def execute(self, value: Any) -> tuple[float]:
        return (float(value),)


class Any2Image:
    """Converts any inputs value to image format.

    A utility node that handles conversion of tensor inputs to a compatible image format for use in
    image processing workflows.

    Args:
        value (Any): The input value to be converted to image format.

    Returns:
        tuple[torch.Tensor]: A single-element tuple containing the image tensor.

    Raises:
        ValueError: If the input value is not a torch.Tensor or cannot be converted to image format.

    Notes:
        - Currently only supports torch.Tensor inputs
        - Input tensors should be in a format compatible with image processing (BWHC format)
        - Future versions may support additional input types and automatic conversion
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": (any_type,),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    CLASS_ID = "any_image"
    DESCRIPTION = """
    Converts any inputs value to image format.
    A utility node that handles conversion of tensor inputs to a compatible image format,
    for use in image processing workflows.
    """

    def execute(self, value: Any) -> tuple[torch.Tensor]:
        if isinstance(value, torch.Tensor):
            return (value,)
        raise ValueError(f"Unsupported type: {type(value)}")


class Any2Any:
    """Passes through any input value unchanged.

    A utility node that acts as a pass-through or identity function, returning the input value
    without any modifications. Useful for workflow organization or debugging.

    Args:
        value (Any): Any input value to be passed through.

    Returns:
        tuple[Any]: A single-element tuple containing the unchanged input value.

    Notes:
        - No validation or transformation is performed on the input
        - Useful as a placeholder or for debugging workflow connections
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": (any_type,),
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("value",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    CLASS_ID = "any2any"

    def execute(self, value: Any) -> tuple[Any]:
        return (value,)


class RGB2HSV:
    """Converts RGB images to HSV color space.

    Transforms images from RGB (Red, Green, Blue) color space to HSV (Hue, Saturation, Value)
    color space while preserving the image structure and dimensions.

    Args:
        image (torch.Tensor): Input RGB image tensor in BWHC format.

    Returns:
        tuple[torch.Tensor]: A single-element tuple containing the HSV image tensor in BWHC format.

    Notes:
        - Input must be in BWHC (Batch, Width, Height, Channels) format
        - RGB values should be normalized to [0, 1] range
        - Output HSV values are in ranges: H[0,360], S[0,1], V[0,1]
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    CLASS_ID = "rgb_hsv"
    DESCRIPTION = """
    Converts RGB images to HSV color space.
    Transforms images from RGB (Red, Green, Blue) color space to HSV (Hue, Saturation, Value)
    color space while preserving the image structure and dimensions.
    """

    def execute(self, image: torch.Tensor) -> tuple[torch.Tensor]:
        image_tensor = TensorImage.from_BWHC(image)
        output = rgb_to_hsv(image_tensor).get_BWHC()
        return (output,)


class RGB2HLS:
    """Converts RGB images to HLS color space.

    Transforms images from RGB (Red, Green, Blue) color space to HLS (Hue, Lightness, Saturation)
    color space while preserving the image structure and dimensions.

    Args:
        image (torch.Tensor): Input RGB image tensor in BWHC format.

    Returns:
        tuple[torch.Tensor]: A single-element tuple containing the HLS image tensor in BWHC format.

    Notes:
        - Input must be in BWHC (Batch, Width, Height, Channels) format
        - RGB values should be normalized to [0, 1] range
        - Output HLS values are in ranges: H[0,360], L[0,1], S[0,1]
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    CLASS_ID = "rgb_hls"
    DESCRIPTION = """
    Converts RGB images to HLS color space.
    Transforms images from RGB (Red, Green, Blue) color space to HLS (Hue, Lightness, Saturation)
    color space while preserving the image structure and dimensions.
    """

    def execute(self, image: torch.Tensor) -> tuple[torch.Tensor]:
        image_tensor = TensorImage.from_BWHC(image)
        output = rgb_to_hls(image_tensor).get_BWHC()
        return (output,)


class RGBA2RGB:
    """Converts RGBA images to RGB format.

    Transforms images from RGBA (Red, Green, Blue, Alpha) format to RGB format by removing the
    alpha channel. Passes through RGB images unchanged.

    Args:
        image (torch.Tensor): Input image tensor in BWHC format (either RGBA or RGB).

    Returns:
        tuple[torch.Tensor]: A single-element tuple containing the RGB image tensor in BWHC format.

    Notes:
        - Input must be in BWHC (Batch, Width, Height, Channels) format
        - Handles both 3-channel (RGB) and 4-channel (RGBA) inputs
        - RGB images are passed through unchanged
        - Alpha channel is removed from RGBA images using rgba_to_rgb conversion
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    CLASS_ID = "rgba2rgb"
    DESCRIPTION = """
    Converts RGBA images to RGB format.
    Transforms images from RGBA (Red, Green, Blue, Alpha) format to RGB format by removing the alpha channel.
    Passes through RGB images unchanged.
    """

    def execute(self, image: torch.Tensor) -> tuple[torch.Tensor]:
        image_tensor = TensorImage.from_BWHC(image)
        if image_tensor.shape[1] == 4:
            image_tensor = rgba_to_rgb(image_tensor)
        output = image_tensor.get_BWHC()
        return (output,)


class RGB2GRAY:
    """Converts RGB images to grayscale format.

    This node transforms RGB color images to single-channel grayscale images using
    standard luminance conversion factors.

    Args:
        image (torch.Tensor): Input RGB image in BWHC format

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing grayscale image in BWHC format

    Notes:
        - Uses standard RGB to grayscale conversion weights
        - Output is single-channel
        - Preserves image dimensions
        - Values remain in [0,1] range
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    DESCRIPTION = """
    Converts RGB images to grayscale format.
    This node transforms RGB color images to single-channel grayscale images
    using standard luminance conversion factors.
    """

    def execute(self, image: torch.Tensor) -> tuple[torch.Tensor]:
        image_tensor = TensorImage.from_BWHC(image)
        output = rgb_to_grayscale(image_tensor).get_BWHC()
        return (output,)


class GRAY2RGB:
    """Converts grayscale images to RGB format.

    This node transforms single-channel grayscale images to three-channel RGB images
    by replicating the grayscale values across channels.

    Args:
        image (torch.Tensor): Input grayscale image in BWHC format

    Returns:
        tuple[torch.Tensor]: Single-element tuple containing RGB image in BWHC format

    Notes:
        - Replicates grayscale values to all RGB channels
        - Output has three identical channels
        - Preserves image dimensions
        - Values remain in [0,1] range
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    DESCRIPTION = """
    Converts grayscale images to RGB format.
    This node transforms single-channel grayscale images to three-channel RGB images
    by replicating the grayscale values across channels.
    """

    def execute(self, image: torch.Tensor) -> tuple[torch.Tensor]:
        output = image
        image_tensor = TensorImage.from_BWHC(image)
        if image_tensor.shape[1] == 1:
            output = grayscale_to_rgb(image_tensor).get_BWHC()
        return (output,)


class PurgeVRAM:
    """Cleans up VRAM by forcing memory deallocation and cache clearing.

    A utility node that performs comprehensive VRAM cleanup by collecting garbage, emptying CUDA cache,
    and unloading models. Useful for managing memory usage in complex workflows.

    Args:
        anything (Any): Any input value that will be passed through unchanged.

    Returns:
        tuple[Any]: A single-element tuple containing the unchanged input value.

    Notes:
        - Calls Python's garbage collector
        - Clears CUDA cache if available
        - Unloads and cleans up ComfyUI models
        - Performs soft cache emptying
        - Input value is passed through unchanged
        - Useful for preventing out-of-memory errors
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "anything": (any_type,),
            },
        }

    RETURN_TYPES = (any_type,)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    OUTPUT_NODE = True
    # DEPRECATED = True
    CLASS_ID = "purge_vram"
    DESCRIPTION = """
    Cleans up VRAM by forcing memory deallocation and cache clearing.
    A utility node that performs comprehensive VRAM cleanup by collecting garbage,
    emptying CUDA cache, and unloading models.
    Useful for managing memory usage in complex workflows.
    """

    def execute(self, anything: Any) -> tuple[Any]:
        clean_memory()
        return (anything,)


class WaitSeconds:
    """Pauses execution for a specified number of seconds.

    A utility node that introduces a delay in the workflow by sleeping for a given duration. This can
    be useful for timing control, pacing operations, or waiting for external processes to complete.

    Args:
        value (Any): Any input value to be returned after the wait period.
        seconds (float): The duration to wait in seconds. Defaults to 1.0 seconds.

    Returns:
        tuple[Any]: A single-element tuple containing the unchanged input value after the wait.

    Notes:
        - The wait time can be adjusted by changing the `seconds` argument.
        - The function uses Python's time.sleep() to implement the delay.
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": (any_type,),
                "seconds": (
                    "FLOAT",
                    {
                        "default": 1.0,
                    },
                ),
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("value",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    DESCRIPTION = """
    Pauses execution for a specified number of seconds.
    A utility node that introduces a delay in the workflow by sleeping for a given duration.
    This can be useful for timing control, pacing operations, or waiting for external processes to complete.
    """

    def execute(self, value: Any, seconds: float = 1.0) -> tuple[Any]:
        time.sleep(seconds)
        return (value,)


class ListBuilder:
    """Builds a list from input elements.

    A node that constructs a list from provided input elements. Used in node-based
    workflows to combine multiple elements into a single list output.

    Args:
        elements (Any): Input elements to combine into a list. The specific types
            accepted are defined in INPUT_TYPES.

    Returns:
        tuple: A tuple containing:
            - list: The constructed list containing all input elements

    Notes:
        - The actual input types and number of elements that can be added to the list
          are defined in the INPUT_TYPES class method
        - This node is typically used in node graph systems to aggregate multiple
          inputs into a single list output
    """

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "num_slots": ([str(i) for i in range(1, 11)], {"default": "1"}),
            },
            "optional": {},
        }

        for i in range(1, 11):
            inputs["optional"].update(
                {
                    f"value_{i}": (any_type, {"forceInput": True}),
                }
            )
        return inputs

    RETURN_TYPES = (
        any_type,
        "LIST",
    )
    RETURN_NAMES = (
        "ANY",
        "LIST",
    )
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    CLASS_ID = "list_builder"
    OUTPUT_IS_LIST = (
        True,
        False,
    )
    DESCRIPTION = """
    Builds a list from input elements.
    A node that constructs a list from provided input elements.
    Used in node-based workflows to combine multiple elements into a single list output.
    """

    def execute(self, num_slots: str = "1", **kwargs) -> tuple[Any, list[Any]]:
        list_stack = []
        for i in range(1, int(num_slots) + 1):
            list_value = kwargs.get(f"value_{i}")
            if list_value is not None:
                list_stack.append(list_value)
        return (
            list_stack,
            list_stack,
        )


class Latent2Dict:
    """Converts a latent tensor representation to a dictionary format.

    Transforms a LATENT input (containing tensor data) into a structured dictionary
    that includes type information, shape, and tensor values.

    Args:
        latent (LATENT): A latent tensor input.

    Returns:
        tuple[dict]: A single-element tuple containing a dictionary with the structure:
            {
                "type": "LATENT",
                "data": {
                    "samples": {
                        "type": str,  # Tensor type name
                        "shape": tuple,  # Tensor dimensions
                        "values": list  # Tensor data as nested lists
                    }
                }
            }
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent": ("LATENT",),
            }
        }

    RETURN_TYPES = ("DICT",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    OUTPUT_NODE = True
    DESCRIPTION = """
    Converts a latent tensor representation to a dictionary format.
    Transforms a LATENT input (containing tensor data) into a structured dictionary
    that includes type information, shape, and tensor values.
    """

    def execute(self, latent: dict) -> tuple[dict]:
        latent_dict = {
            "type": "LATENT",
            "data": {
                "samples": {
                    "type": str(type(latent["samples"]).__name__),
                    "shape": latent["samples"].shape,
                    "values": latent["samples"].tolist(),
                }
            },
        }

        return (latent_dict,)


class Dict2Latent:
    """Converts a dictionary representation back to a latent tensor format.

    Transforms a structured dictionary containing tensor data back into the LATENT
    format used by the system.

    Args:
        dict (DICT): A dictionary containing tensor data in the format:
            {
                "type": "LATENT",
                "data": {
                    "samples": {
                        "type": str,  # Tensor type name
                        "shape": tuple,  # Tensor dimensions
                        "values": list  # Tensor data as nested lists
                    }
                }
            }

    Returns:
        tuple[LATENT]: A single-element tuple containing the reconstructed latent
            tensor in the format: {"samples": tensor}

    Raises:
        ValueError: If the input dictionary is not of type "LATENT" or contains an
            unsupported tensor type.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dict": ("DICT",),
            }
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    OUTPUT_NODE = True
    DESCRIPTION = """
    Converts a dictionary representation back to a latent tensor format.
    Transforms a structured dictionary containing tensor data back into the LATENT
    format used by the system.
    """

    def execute(self, dict: dict) -> tuple[dict]:
        if dict.get("type") != "LATENT":
            raise ValueError("Input dictionary is not a LATENT type")

        samples_data = dict["data"]["samples"]
        tensor_type = samples_data["type"]
        if "Tensor" in tensor_type or "GGMLTensor" in tensor_type or "TensorImage" in tensor_type:
            tensor_data = torch.tensor(samples_data["values"])
            tensor_data = tensor_data.reshape(samples_data["shape"])
        else:
            raise ValueError(f"Unsupported tensor type: {tensor_type}")

        latent = {"samples": tensor_data}

        return (latent,)


class InputListToList:
    """Converts a list input to a list as as single output.

    A utility node that takes an input list and returns a single list containing all the inputs.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"list": (any_type,)},
        }

    RETURN_TYPES = ("LIST",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    OUTPUT_NODE = True
    INPUT_IS_LIST = True
    CLASS_ID = "input_list_to_list"
    DESCRIPTION = """
    Converts a list input to a list as a single output.
    A utility node that takes an input list and returns a single list containing all the inputs.
    """

    def execute(self, list: list[Any]) -> tuple[list[Any]]:
        return (list,)


class ListToOutputList:
    """Converts a list input to a list as a single output.

    A utility node that takes a list and returns an output list for iterations.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"list": ("LIST",)},
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("ANY",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    OUTPUT_IS_LIST = (True,)
    CLASS_ID = "list_to_output_list"
    DESCRIPTION = """
    Converts a list input to a list as a single output.
    A utility node that takes a list and returns an output list for iterations.
    """

    def execute(self, list: list[Any]) -> tuple[list[Any]]:
        return (list,)


class BatchBuilder:
    """Builds a batch from input images.

    A node that constructs a batch from provided input images usign the first one as the base. Used in node-based
    workflows to combine multiple images into a single batch output.

    Args:
        images (Image): Input images to combine into a batch.

    Returns:
        tuple: A tuple containing:
            - batch: The constructed batch containing all input images

    Notes:
        - This node is typically used in node graph systems to
        aggregate multiple image inputs into a single batch output
    """

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "num_slots": ([str(i) for i in range(1, 11)], {"default": "1"}),
            },
            "optional": {},
        }

        for i in range(1, 11):
            inputs["optional"].update(
                {
                    f"value_{i}": ("IMAGE, MASK", {"forceInput": True}),
                }
            )
        return inputs

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("ANY",)
    FUNCTION = "execute"
    CATEGORY = UTILS_CAT
    CLASS_ID = "batch_builder"
    DESCRIPTION = """
    Builds a batch from input images.
    A node that constructs a batch from provided input images usign the first one as the base.
    Used in node-based workflows to combine multiple images into a single batch output.
    """

    def execute(self, num_slots: str = "1", **kwargs) -> tuple[torch.Tensor]:
        if f"value_{int(num_slots)}" not in kwargs.keys():
            raise ValueError("Number of inputs is not equal to number of slots")

        base = kwargs.get("value_1")
        if base is None:
            raise ValueError("Base image is not provided")
        base_shape = TensorImage.from_BWHC(base).shape
        images = []

        for i in range(1, int(num_slots) + 1):
            image = kwargs.get(f"value_{i}")
            if image is None:
                raise ValueError(f"Image in value_{i} is not provided")
            image_shape = TensorImage.from_BWHC(image).shape

            # Ensure mask tensors are properly shaped (add channels dimension if needed)
            if len(image_shape) == 3 or (len(image_shape) == 4 and image_shape[1] == 1):
                # For masks, ensure they're in the correct format (B,1,H,W)
                if len(image.shape) == 3:
                    image = image.unsqueeze(3)  # Add channel dimension

            if base_shape[1:] == image_shape[1:]:
                images.append(image)
            else:
                raise ValueError(f"Image/Mask in value_{i} is not the same shape as the image/mask in value_1")

        images = torch.cat(images, dim=0)
        return (images,)
