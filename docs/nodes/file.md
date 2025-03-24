# File Nodes

## Base64FromImage

Converts ComfyUI image tensors to base64-encoded strings.

Transforms image tensors from ComfyUI's format into base64-encoded strings, suitable for web
transmission or storage in text format.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | image | `IMAGE` |  |  |

### Returns

| Name | Type |
|------|------|
| string | `STRING` |


??? note "Source code"

    ```python
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
        DESCRIPTION = """
        Converts images to base64-encoded strings (PNG format).
        Creates text representations of images suitable for web transmission, APIs,
        or text-based storage without data URL prefix."""

        def execute(self, image: torch.Tensor) -> tuple[str]:
            images = TensorImage.from_BWHC(image)
            output = images.get_base64()
            return (output,)
    ```

## FileLoader

Processes string input into ComfyUI-compatible file data.

Converts JSON-formatted string data into file references with proper paths for ComfyUI processing.
Handles both single files and multiple files separated by '&&'.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | value | `STRING` |  |  |

### Returns

| Name | Type |
|------|------|
| file | `FILE` |


??? note "Source code"

    ```python
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
        DESCRIPTION = """
        Converts JSON-formatted strings into ComfyUI-compatible file references.
        Handles both single and multiple files (separated by '&&').
        Automatically prepends proper input folder paths.
        """

        def execute(self, value: str = "") -> tuple[list]:
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
    ```

## ImageFromWeb

Fetches and converts web images to ComfyUI-compatible tensors.

Downloads an image from a URL and processes it into ComfyUI's expected tensor format. Handles both RGB
and RGBA images with automatic mask generation for transparency.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | url | `STRING` | URL HERE |  |

### Returns

| Name | Type |
|------|------|
| image | `IMAGE` |
| mask | `MASK` |


??? note "Source code"

    ```python
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
        DESCRIPTION = """
        Downloads and converts web images to ComfyUI-compatible tensors.
        Fetches images from URLs and processes them with automatic mask generation for transparency.
        Supports common web image formats.
        """

        def execute(self, url: str = "URL HERE") -> tuple[torch.Tensor, torch.Tensor]:
            img_arr = TensorImage.from_web(url)
            return image_array_to_tensor(img_arr)
    ```

## ImageFromBase64

Converts base64 image strings to ComfyUI-compatible tensors.

Processes base64-encoded image data into tensor format suitable for ComfyUI operations. Handles
both RGB and RGBA images with proper mask generation.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | base64 | `STRING` | BASE64 HERE | multiline=True |

### Returns

| Name | Type |
|------|------|
| image | `IMAGE` |
| mask | `MASK` |


??? note "Source code"

    ```python
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
            return {"required": {"base64": ("STRING", {"default": "BASE64 HERE", "multiline": True})}}

        RETURN_TYPES = ("IMAGE", "MASK")
        FUNCTION = "execute"
        CATEGORY = FILE_CAT
        DEPRECATED = True
        DESCRIPTION = """
        Converts base64-encoded image strings to ComfyUI-compatible tensors with masks.
        Handles both RGB and RGBA images, extracting transparency as mask.
        Note: This node is deprecated.
        """

        def execute(self, base64: str = "BASE64 HERE") -> tuple[torch.Tensor, torch.Tensor]:
            img_arr = TensorImage.from_base64(base64)
            return image_array_to_tensor(img_arr)
    ```

## File2ImageList

Converts file references to a list of image tensors.

Processes a list of file references, extracting and converting supported image files into
ComfyUI-compatible tensor format.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | files | `FILE` |  |  |

### Returns

| Name | Type |
|------|------|
| image | `IMAGE` |


??? note "Source code"

    ```python
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
        DESCRIPTION = """
        Converts file references to a list of image tensors. Processes multiple files,
        extracting supported image formats (PNG, JPG, JPEG, TIFF, BMP) into ComfyUI-compatible format.
        """

        def execute(self, files: list[dict]) -> tuple[list[torch.Tensor]]:
            images_list = []
            for file in files:
                mimetype = file["type"]
                extension = file["name"].lower().split(".")[-1]
                possible_extensions = ["png", "jpg", "jpeg", "tiff", "tif", "bmp"]
                if mimetype.startswith("image") and extension in possible_extensions:
                    images_list.append(TensorImage.from_local(file["name"]).get_BWHC())

            return (images_list,)
    ```

## File2List

Converts file input to a standardized list format.

Processes file input data into a consistent list format for further ComfyUI operations.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | files | `FILE` |  |  |

### Returns

| Name | Type |
|------|------|
| list | `LIST` |


??? note "Source code"

    ```python
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
        DESCRIPTION = """
        Converts file input to a standardized list format.
        Processes file data into a consistent structure while preserving metadata and original order.
        Enables further list-based operations on file collections.
        """

        def execute(self, files: list[dict]) -> tuple[list[dict]]:
            return (files,)
    ```

## FolderLoader

Processes folder paths into ComfyUI-compatible file data.

Converts folder path information into properly formatted file references for ComfyUI processing.
Supports both single and multiple folder paths.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | value | `STRING` |  |  |

### Returns

| Name | Type |
|------|------|
| file | `FILE` |


??? note "Source code"

    ```python
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
        DESCRIPTION = """
        Converts folder path information into ComfyUI-compatible file references.
        Handles both single and multiple folders (separated by '&&').
        Automatically prepends proper input folder paths while maintaining folder structure.
        """

        def execute(self, value: str = "") -> tuple[list]:
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

    ```
