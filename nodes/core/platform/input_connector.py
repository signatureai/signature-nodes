import os

from signature_core.connectors.google_connector import GoogleConnector

from ...categories import PLATFORM_IO_CAT
from ...shared import BASE_COMFY_DIR


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
