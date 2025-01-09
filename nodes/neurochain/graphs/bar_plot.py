import matplotlib

from ...categories import GRAPH_CAT

matplotlib.use("Agg")
import io
import random

import folder_paths  # type: ignore
import matplotlib.pyplot as plt
from signature_core.functional.color import rgba_to_rgb
from signature_core.img.tensor_image import TensorImage

from nodes import SaveImage  # type: ignore


class BarPlot(SaveImage):
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + "".join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 1

    @classmethod
    def INPUT_TYPES(s):  # type: ignore
        return {
            "required": {
                "values": ("LIST", {}),
                "title": ("STRING", {"default": "Bar Plot"}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "process"
    CATEGORY = GRAPH_CAT
    OUTPUT_NODE = True

    def process(self, values: list, title: str, filename_prefix="Signature", prompt=None, extra_pnginfo=None):
        fig, ax = plt.subplots()

        value_counts = {}
        for item in values:
            label = str(item)
            value_counts[label] = value_counts.get(label, 0) + 1

        ax.bar(value_counts.keys(), value_counts.values())

        ax.set_ylabel("Frequency")
        ax.set_title(title)

        buf = io.BytesIO()
        fig.savefig(
            buf,
        )
        buf.seek(0)

        plot_image = rgba_to_rgb(TensorImage.from_bytes(buffer=buf.getvalue()))
        output = plot_image.get_BWHC()

        result = self.save_images(output, filename_prefix, prompt, extra_pnginfo)
        result.update({"result": (output,)})
        return result
