import json
import os
import time
from datetime import datetime

import torch
from signature_core.connectors.google_connector import GoogleConnector
from signature_core.functional.transform import cutout
from signature_core.img.tensor_image import TensorImage
from uuid_extensions import uuid7str

from .categories import PLATFORM_IO_CAT
from .shared import BASE_COMFY_DIR, any_type


class InputImage:
    """Processes and validates image inputs from various sources for the platform.

    This class handles image input processing, supporting both single and multiple images from URLs. It includes functionality for alpha channel management and mask generation.

    Args:
        title (str): Display title for the input node. Defaults to "Input Image".
        subtype (str): Type of input - either "image" or "mask".
        required (bool): Whether the input is required. Defaults to True.
        include_alpha (bool): Whether to preserve alpha channel. Defaults to False.
        multiple (bool): Allow multiple image inputs. Defaults to False.
        value (str): Image data as URL.
        metadata (str): JSON string containing additional metadata. Defaults to "{}".
        fallback (any): Optional fallback value if no input is provided.

    Returns:
        tuple[list]: A tuple containing a list of processed images as torch tensors in BWHC format.

    Raises:
        ValueError: If value is not a string, subtype is invalid, or no valid input is found.

    Notes:
        - URLs must start with "http" to be recognized
        - Multiple images can be provided as comma-separated values
        - Alpha channels are removed by default unless include_alpha is True
        - Mask inputs are automatically converted to grayscale
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "title": ("STRING", {"default": "Input Image"}),
                "subtype": (["image", "mask"], {"default": "image"}),
                "required": ("BOOLEAN", {"default": True}),
                "include_alpha": ("BOOLEAN", {"default": False}),
                "multiple": ("BOOLEAN", {"default": False}),
                "value": (
                    "STRING",
                    {
                        "default": "https://www.example.com/images/sample.jpg",
                        "multiline": True,
                    },
                ),
                "metadata": ("STRING", {"default": "{}", "multiline": True}),
            },
            "optional": {
                "fallback": (any_type,),
            },
        }

    RETURN_TYPES = (any_type,)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT
    OUTPUT_IS_LIST = (True,)
    DESCRIPTION = """# InputImage Node - Your Gateway for Images in ComfyUI

    ## What it Does 🎨
    This node is your main entry point for bringing images into ComfyUI workflows. Think of it as a universal image
    loader that can handle:
    - Images from web URLs (anything starting with "http")
    - Single images or multiple images at once
    - Regular images and masks
    - Images with or without transparency

    ## How to Use It 🚀

    ### Basic Settings
    - **Title**: Just a label for your node (default: "Input Image")
    - **Subtype**: Choose between:
        - `image` - for regular images
        - `mask` - for masks (automatically converts to grayscale)
    - **Include Alpha**: Toggle transparency handling
        - OFF: Removes transparency (default)
        - ON: Keeps transparency channel
    - **Multiple**: Allow multiple images
        - OFF: Takes only first image (default)
        - ON: Processes all provided images

    ### Input Methods
    1. Web Images: Just paste the image URL (must start with "http")
    2. Multiple Images: With "Multiple" enabled, separate URLs with spaces
    3. Fallback: Optional backup image if main input fails

    ## Tips & Tricks 💡
    - For batch processing, enable "Multiple" and input several URLs separated by spaces
    - When working with masks, set "subtype" to "mask" for automatic grayscale conversion
    - If you need transparency in your workflow, make sure to enable "Include Alpha"
    - The node automatically handles various image formats and color spaces

    ## Output
    - Outputs images in the format ComfyUI expects (BCHW tensor format)
    - Perfect for feeding into other ComfyUI nodes like upscalers, ControlNet, or image processors

    Think of this node as your universal image importer - it handles all the technical conversion stuff so you can focus
    on the creative aspects of your workflow! 🎨✨"""

    # TODO: confirm if title, required and metadata inputs are needed
    def execute(
        self,
        title: str = "Input Image",
        subtype: str = "image",
        required: bool = True,
        include_alpha: bool = False,
        multiple: bool = False,
        value: str = "",
        metadata: str = "{}",
        fallback: any = None,
    ) -> tuple[list[torch.Tensor]]:
        def post_process(output: TensorImage, include_alpha: bool) -> TensorImage:
            if output.shape[1] not in [3, 4]:
                if len(output.shape) == 2:  # (H,W)
                    output = TensorImage(output.unsqueeze(0).unsqueeze(0).expand(-1, 3, -1, -1))
                elif len(output.shape) == 3:  # (B,H,W)
                    output = TensorImage(output.unsqueeze(1).expand(-1, 3, -1, -1))
                elif len(output.shape) == 4 and output.shape[1] == 1:  # (B,1,H,W)
                    output = TensorImage(output.expand(-1, 3, -1, -1))
                else:
                    raise ValueError(f"Unsupported shape: {output.shape}")
            else:
                if not include_alpha and output.shape[1] == 4:
                    rgb = TensorImage(output[:, :3, :, :])
                    alpha = TensorImage(output[:, -1, :, :])
                    output, _ = cutout(rgb, alpha)
            return output

        def process_value(value: str, multiple: bool) -> list[str]:
            if not value:
                return []
            if " " in value:
                items = value.split(" ")
                return items if multiple else [items[0]]
            return [value]

        def load_image(url: str) -> TensorImage:
            if not url:
                raise ValueError("Empty input string")

            try:
                if url.startswith("http"):
                    return TensorImage.from_web(url)
            except Exception as e:
                raise ValueError(f"Unsupported input format: {url}") from e

        value_list = process_value(value, multiple)
        outputs: list[torch.Tensor] = []

        # Process each input value
        for item in value_list:
            if isinstance(item, str):
                try:
                    output = load_image(item)
                    outputs.append(output)
                except ValueError as e:
                    if not outputs:
                        raise e

        if len(outputs) == 0:
            if fallback is None:
                raise ValueError("No input found and no fallback provided")
            outputs.append(TensorImage.from_BWHC(fallback))

        for i, output in enumerate(outputs):
            if not isinstance(output, TensorImage):
                raise ValueError(f"Output {i} must be a TensorImage")

            if subtype == "mask":
                outputs[i] = output.get_grayscale().get_BWHC()
            else:
                outputs[i] = post_process(output, include_alpha).get_BWHC()
        return (outputs,)


class InputConnector:
    """Manages file downloads from external services using authentication tokens.

    Handles connections to external services (currently Google Drive) to download files using provided
    authentication tokens and file identifiers.

    Args:
        title (str): Display title for the connector. Defaults to "Input Connector".
        subtype (str): Service type, currently only supports "google_drive".
        required (bool): Whether the input is required. Defaults to True.
        override (bool): Whether to override existing files. Defaults to False.
        token (str): Authentication token for the service.
        mime_type (str): Expected MIME type of the file. Defaults to "image/png".
        value (str): File identifier for the service.
        metadata (str): JSON string containing additional metadata. Defaults to "{}".

    Returns:
        tuple[str]: A tuple containing the path to the downloaded file.

    Raises:
        ValueError: If token, value, mime_type are not strings or override is not boolean.

    Notes:
        - Files are downloaded to the ComfyUI input directory
        - Supports Google Drive integration with proper authentication
        - Can be extended to support other services in the future
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "title": ("STRING", {"default": "Input Connector"}),
                "subtype": (["google_drive"],),
                "required": ("BOOLEAN", {"default": True}),
                "override": ("BOOLEAN", {"default": False}),
                "token": ("STRING", {"default": ""}),
                "mime_type": ("STRING", {"default": "image/png"}),
                "value": ("STRING", {"default": ""}),
                "metadata": ("STRING", {"default": "{}", "multiline": True}),
            },
        }

    RETURN_TYPES = ("FILE",)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT
    DEPRECATED = True

    # TODO: confirm if title, subtype required and metadata inputs are needed
    def execute(  # nosec: B107
        self,
        title: str = "Input Connector",
        subtype: str = "google_drive",
        required: bool = True,
        override: bool = False,
        token: str = "",
        mime_type: str = "image/png",
        value: str = "",
        metadata: str = "{}",
    ):
        connector = GoogleConnector(token=token)
        input_folder = os.path.join(BASE_COMFY_DIR, "input")
        data = connector.download(
            file_id=value,
            mime_type=mime_type,
            output_path=input_folder,
            override=override,
        )
        return (data,)


class InputText:
    """Processes text input with fallback support.

    Handles text input processing with support for different subtypes and optional fallback values
    when input is empty.

    Args:
        title (str): Display title for the text input. Defaults to "Input Text".
        subtype (str): Type of text - "string", "positive_prompt", or "negative_prompt".
        required (bool): Whether the input is required. Defaults to True.
        value (str): The input text value.
        metadata (str): JSON string containing additional metadata. Defaults to "{}".
        fallback (str): Optional fallback text if input is empty.

    Returns:
        tuple[str]: A tuple containing the processed text value.

    Raises:
        ValueError: If value or fallback are not strings.

    Notes:
        - Empty inputs will use the fallback value if provided
        - Supports multiline text input
        - Special handling for prompt-type inputs
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "title": ("STRING", {"default": "Input Text"}),
                "subtype": (["string"],),
                "required": ("BOOLEAN", {"default": True}),
                "value": ("STRING", {"multiline": True, "default": ""}),
                "metadata": ("STRING", {"default": "{}", "multiline": True}),
            },
            "optional": {
                "fallback": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT

    # TODO: confirm if title, subtype required and metadata inputs are needed
    def execute(
        self,
        title: str = "Input Text",
        subtype: str = "string",
        required: bool = True,
        value: str = "",
        metadata: str = "{}",
        fallback: str = "",
    ) -> tuple[str]:
        if fallback and value == "":
            value = fallback
        return (value,)


class InputNumber:
    """Processes numeric inputs with type conversion.

    Handles numeric input processing with support for both integer and float values, including
    automatic type conversion based on the specified subtype.

    Args:
        title (str): Display title for the number input. Defaults to "Input Number".
        subtype (str): Type of number - either "float" or "int".
        required (bool): Whether the input is required. Defaults to True.
        value (float): The input numeric value. Defaults to 0.
        metadata (str): JSON string containing additional metadata. Defaults to "{}".

    Returns:
        tuple[Union[int, float]]: A tuple containing the processed numeric value.

    Raises:
        ValueError: If value is not numeric or subtype is invalid.

    Notes:
        - Automatically converts between float and int based on subtype
        - Maintains numeric precision during conversion
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "title": ("STRING", {"default": "Input Number"}),
                "subtype": (["float", "int"],),
                "required": ("BOOLEAN", {"default": True}),
                "value": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": -18446744073709551615,
                        "max": 18446744073709551615,
                        "step": 0.1,
                    },
                ),
                "metadata": ("STRING", {"default": "{}", "multiline": True}),
            },
        }

    RETURN_TYPES = (any_type,)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT

    # TODO: confirm if title and metadata inputs are needed
    def execute(
        self,
        title: str = "Input Number",
        subtype: str = "float",
        required: bool = True,
        value: float = 0,
        metadata: str = "{}",
    ) -> tuple[float]:
        if subtype == "int":
            value = round(value)
        elif subtype == "float":
            value = float(value)
        return (value,)


class InputBoolean:
    """Processes boolean inputs for the platform.

    Handles boolean input processing with validation and type checking.

    Args:
        title (str): Display title for the boolean input. Defaults to "Input Boolean".
        subtype (str): Must be "boolean".
        required (bool): Whether the input is required. Defaults to True.
        value (bool): The input boolean value. Defaults to False.
        metadata (str): JSON string containing additional metadata. Defaults to "{}".

    Returns:
        tuple[bool]: A tuple containing the boolean value.

    Raises:
        ValueError: If value is not a boolean.

    Notes:
        - Simple boolean validation and processing
        - Returns original boolean value without modification
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "title": ("STRING", {"default": "Input Boolean"}),
                "subtype": (["boolean"], {"default": "boolean"}),
                "required": ("BOOLEAN", {"default": True}),
                "value": ("BOOLEAN", {"default": False}),
                "metadata": ("STRING", {"default": "{}", "multiline": True}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT

    # TODO: confirm if title, subtype, and metadata inputs are needed
    def execute(
        self,
        title: str = "Input Boolean",
        subtype: str = "boolean",
        required: bool = True,
        value: bool = False,
        metadata: str = "{}",
    ) -> tuple[bool]:
        return (value,)


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


class PlatformEnvs:
    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "environment": (["production", "staging", "develop"],),
            },
        }

    RETURN_TYPES = (
        "STRING",
        "STRING",
    )
    RETURN_NAMES = (
        "ORG_ID",
        "ORG_TOKEN",
    )
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT

    def execute(self, **kwargs):
        env = kwargs.get("environment") or ""
        org_id = "ORG_ID" if env == "production" else f"{env.upper()}_ORG_ID"
        org_token = "ORG_TOKEN" if env == "production" else f"{env.upper()}_ORG_TOKEN"
        ORG_ID = os.environ.get(org_id)
        ORG_TOKEN = os.environ.get(org_token)
        return (
            ORG_ID,
            ORG_TOKEN,
        )


class Report:
    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "value": (any_type,),
                "report": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("value",)
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT
    OUTPUT_NODE = True

    def execute(self, value, report):
        data = {"type": "string", "value": report}
        return {"ui": {"signature_report": [data]}, "result": (value,)}
