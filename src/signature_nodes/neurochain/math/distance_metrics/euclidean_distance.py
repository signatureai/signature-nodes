import numpy as np

from ....categories import DIST_CAT


class EuclideanDistance:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vector_a": ("LIST", {}),
                "vector_b": ("LIST", {}),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("distance",)
    FUNCTION = "process"
    CATEGORY = DIST_CAT
    OUTPUT_NODE = True

    def process(self, vector_a: list, vector_b: list):
        def euclidean_distance(a, b):
            return np.sqrt(np.sum((np.array(a) - np.array(b)) ** 2))

        output = euclidean_distance(vector_a, vector_b)
        return (output,)
