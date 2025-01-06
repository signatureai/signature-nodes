import numpy as np

from ....categories import DIST_CAT


class CosineSimilarity:
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
        def cosine_similarity(a, b):
            a = np.array(a)
            b = np.array(b)
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        output = cosine_similarity(vector_a, vector_b)
        return (output,)
