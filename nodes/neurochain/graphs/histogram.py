import matplotlib

matplotlib.use("Agg")
import io

import matplotlib.pyplot as plt
from signature_core.functional.color import rgba_to_rgb
from signature_core.img.tensor_image import TensorImage

from ...categories import GRAPH_CAT


class Histogram:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "data": ("LIST", {}),
                "bins": ("INT", {"default": 10, "min": 1, "max": 100}),
                "title": ("STRING", {"default": "Histogram"}),
                "x_label": ("STRING", {"default": "Value"}),
                "y_label": ("STRING", {"default": "Frequency"}),
            },
            "optional": {
                "color": ("STRING", {"default": "blue"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("histogram_image",)
    FUNCTION = "process"
    CATEGORY = GRAPH_CAT
    OUTPUT_NODE = True

    def process(self, data: list, bins: int, title: str, x_label: str, y_label: str, color: str = "blue"):
        # Create the histogram
        fig, ax = plt.subplots()
        ax.hist(data, bins=bins, color=color, edgecolor="black")

        # Set labels and title
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)

        # Save the plot to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)

        plot_image = rgba_to_rgb(TensorImage.from_bytes(buffer=buf.getvalue()))
        output = plot_image.get_BWHC()

        return (output,)
