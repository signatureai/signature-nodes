import json
import os
import time
from datetime import datetime

import torch
from signature_core.img.tensor_image import TensorImage
from uuid_extensions import uuid7str

from ...categories import PLATFORM_IO_CAT
from ...shared import BASE_COMFY_DIR, any_type


class Output:
    """Manages output processing and file saving for various data types.

    Handles the processing and saving of different output types including images, masks, numbers, and
    strings. Includes support for thumbnail generation and metadata management.

    Args:
        title (str): Display title for the output. Defaults to "Output Image".
        subtype (str): Type of output - "image", "mask", "int", "float", "string", or "dict".
        metadata (str): JSON string containing additional metadata.
        value (any): The value to output.
        output_path (str): Path for saving outputs. Defaults to "output".

    Returns:
        dict: UI configuration with signature_output containing processed results.

    Raises:
        ValueError: If inputs are invalid or output type is unsupported.

    Notes:
        - Automatically generates thumbnails for image outputs
        - Saves images with unique filenames including timestamps
        - Supports batch processing of multiple outputs
        - Creates both full-size PNG and compressed JPEG thumbnails
        - Handles various data types with appropriate serialization
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "title": ("STRING", {"default": "Output Image"}),
                "subtype": (["image", "mask", "int", "float", "string", "dict"],),
                "metadata": ("STRING", {"default": "{}", "multiline": True}),
                "value": (any_type,),
            },
            "hidden": {
                "output_path": ("STRING", {"default": "output"}),
            },
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    INPUT_IS_LIST = True
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT
    DESCRIPTION = "Manages output processing and file saving for various data types. Handles the processing and saving of different output types including images, masks, numbers, and strings. Includes support for thumbnail generation and metadata management."

    @classmethod
    def IS_CHANGED(cls, **kwargs):  # type: ignore
        return time.time()

    def __save_outputs(self, **kwargs) -> dict | None:
        img = kwargs.get("img")
        if not isinstance(img, (torch.Tensor, TensorImage)):
            raise ValueError("Image must be a tensor or TensorImage")

        title = kwargs.get("title", "")
        if not isinstance(title, str):
            title = str(title)

        subtype = kwargs.get("subtype", "image")
        if not isinstance(subtype, str):
            subtype = str(subtype)

        thumbnail_size = kwargs.get("thumbnail_size", 1024)
        if not isinstance(thumbnail_size, int):
            try:
                thumbnail_size = int(thumbnail_size)
            except (ValueError, TypeError):
                thumbnail_size = 1024

        output_dir = kwargs.get("output_dir", "output")
        if not isinstance(output_dir, str):
            output_dir = str(output_dir)

        metadata = kwargs.get("metadata", "")
        if not isinstance(metadata, str):
            metadata = str(metadata)

        current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"signature_{current_time_str}_{uuid7str()}.png"
        save_path = os.path.join(output_dir, file_name)
        if os.path.exists(save_path):
            file_name = f"signature_{current_time_str}_{uuid7str()}_{uuid7str()}.png"
            save_path = os.path.join(output_dir, file_name)

        output_img = img if isinstance(img, TensorImage) else TensorImage(img)

        thumbnail_img = output_img.get_resized(thumbnail_size)
        thumbnail_path = save_path.replace(".png", "_thumbnail.jpeg")
        thumbnail_file_name = file_name.replace(".png", "_thumbnail.jpeg")
        thumbnail_saved = thumbnail_img.save(thumbnail_path)

        image_saved = output_img.save(save_path)

        if image_saved and thumbnail_saved:
            return {
                "title": title,
                "type": subtype,
                "metadata": metadata,
                "value": file_name,
                "thumbnail": thumbnail_file_name if thumbnail_saved else None,
            }

        return None

    def execute(self, **kwargs):
        title_list = kwargs.get("title")
        if not isinstance(title_list, list):
            raise ValueError("Title must be a list")
        metadata_list = kwargs.get("metadata")
        if not isinstance(metadata_list, list):
            raise ValueError("Metadata must be a list")
        subtype_list = kwargs.get("subtype")
        if not isinstance(subtype_list, list):
            raise ValueError("Subtype must be a list")
        output_path_list = kwargs.get("output_path")
        if not isinstance(output_path_list, list):
            output_path_list = ["output"] * len(title_list)
        value_list = kwargs.get("value")
        if not isinstance(value_list, list):
            raise ValueError("Value must be a list")
        main_subtype = subtype_list[0]
        supported_types = ["image", "mask", "int", "float", "string", "dict"]
        if main_subtype not in supported_types:
            raise ValueError(f"Unsupported output type: {main_subtype}")

        results = []
        thumbnail_size = 1024
        for idx, item in enumerate(value_list):
            title = title_list[idx]
            metadata = metadata_list[idx]
            output_dir = os.path.join(BASE_COMFY_DIR, output_path_list[idx])
            if isinstance(item, torch.Tensor):
                if main_subtype in ["image", "mask"]:
                    tensor_images = TensorImage.from_BWHC(item.to("cpu"))
                    for img in tensor_images:
                        result = self.__save_outputs(
                            img=img,
                            title=title,
                            subtype=main_subtype,
                            thumbnail_size=thumbnail_size,
                            output_dir=output_dir,
                            metadata=metadata,
                        )
                        if result:
                            results.append(result)
                else:
                    raise ValueError(f"Unsupported output type: {type(item)}")
            else:
                value_json = json.dumps(item) if main_subtype == "dict" else item
                results.append(
                    {
                        "title": title,
                        "type": main_subtype,
                        "metadata": metadata,
                        "value": value_json,
                    }
                )
        return {"ui": {"signature_output": results}}
