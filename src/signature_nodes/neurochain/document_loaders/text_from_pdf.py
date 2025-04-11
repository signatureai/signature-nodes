from neurochain.document_loaders.text_from_pdf import (
    TextFromPdf as TextFromPdfNeurochain,
)

from ...categories import LOADERS_CAT


class TextFromPdf:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING",),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = LOADERS_CAT

    def execute(self, **kwargs):
        path = kwargs.get("path")
        if path is None:
            raise ValueError("Path is required")

        text_from_pdf = TextFromPdfNeurochain()
        text = text_from_pdf.extract(path)

        return (text,)
