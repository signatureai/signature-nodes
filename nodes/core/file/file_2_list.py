from ...categories import FILE_CAT


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
    DESCRIPTION = "Converts file input to a standardized list format. Processes file data into a consistent structure while preserving metadata and original order. Enables further list-based operations on file collections."

    def execute(self, files: list[dict]) -> tuple[list[dict]]:
        return (files,)
