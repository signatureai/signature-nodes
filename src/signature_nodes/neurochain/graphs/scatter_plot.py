import matplotlib

matplotlib.use("Agg")
import io

import matplotlib.pyplot as plt
import numpy as np
from signature_core.functional.color import rgba_to_rgb
from signature_core.img.tensor_image import TensorImage

from ...categories import GRAPH_CAT


class ScatterPlot:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x_values": ("LIST", {}),
                "y_values": ("LIST", {}),
                "labels": ("LIST", {}),  # New input for labels
                "title": ("STRING", {"default": "Scatter Plot"}),
                "x_label": ("STRING", {"default": "X"}),
                "y_label": ("STRING", {"default": "Y"}),
            },
            "optional": {
                "marker": ("STRING", {"default": "o"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "process"
    CATEGORY = GRAPH_CAT
    OUTPUT_NODE = True

    def process(
        self, x_values: list, y_values: list, labels: list, title: str, x_label: str, y_label: str, marker: str = "o"
    ):
        if len(x_values) != len(y_values) or len(x_values) != len(labels):
            raise ValueError(
                f"Length of x_values ({len(x_values)}), y_values ({len(y_values)}), "
                f"and labels ({len(labels)}) must match"
            )

        # Create the scatter plot
        fig, ax = plt.subplots()

        # Get unique labels and assign colors
        unique_labels = list(set(labels))
        colors = matplotlib.colormaps["rainbow"](np.linspace(0, 1, len(unique_labels)))
        label_to_color = dict(zip(unique_labels, colors))

        # Plot points for each unique label
        for label in unique_labels:
            mask = [label == label for label in labels]
            x = [x_values[i] for i in range(len(x_values)) if mask[i]]
            y = [y_values[i] for i in range(len(y_values)) if mask[i]]
            ax.scatter(x, y, color=label_to_color[label], marker=marker, label=label)

        # Add legend (only showing unique labels)
        ax.legend()

        # Set labels and title
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)

        # Save the plot to a buffer
        buf = io.BytesIO()
        fig.savefig(buf)
        buf.seek(0)

        # Convert to tensor image
        plot_image = rgba_to_rgb(TensorImage.from_bytes(buffer=buf.getvalue()))
        output = plot_image.get_BWHC()
        return (output,)
