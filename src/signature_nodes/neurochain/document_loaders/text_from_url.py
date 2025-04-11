from neurochain.document_loaders.text_from_url import TextFromUrl as TextFromUrlNeurochain

from ...categories import LOADERS_CAT


class TextFromUrl:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "process"
    CATEGORY = LOADERS_CAT
    OUTPUT_NODE = True

    def process(self, url: str):
        extractor = TextFromUrlNeurochain()
        return (extractor.extract(url),)
