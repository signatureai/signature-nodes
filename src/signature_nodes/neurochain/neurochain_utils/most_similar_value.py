import os

import folder_paths  # type: ignore
from huggingface_hub import snapshot_download
from neurochain.agents.text_similarity import TextSimilarity
from transformers.models.auto.modeling_auto import AutoModel
from transformers.models.auto.tokenization_auto import AutoTokenizer

from ...categories import NEUROCHAIN_UTILS_CAT

SIG_EMBEDDINGS_DIR = "sig_embeddings"
DEFAULT_MODEL = {
    "repository_id": "sentence-transformers/all-MiniLM-L6-v2",
    "model_name": "all-MiniLM-L6-v2",
    "files": [
        "config.json",
        "model.safetensors",
        "special_tokens_map.json",
        "tokenizer_config.json",
        "tokenizer.json",
        "vocab.txt",
    ],
}


class MostSimilarValue:
    @classmethod
    def INPUT_TYPES(cls):
        embeddings_path = os.path.join(folder_paths.models_dir, SIG_EMBEDDINGS_DIR)
        if not os.path.exists(embeddings_path):
            os.makedirs(embeddings_path)
        model_path = os.path.join(embeddings_path, DEFAULT_MODEL["model_name"])
        if not os.path.exists(model_path):
            snapshot_download(
                repo_id=DEFAULT_MODEL["repository_id"],
                local_dir=model_path,
                allow_patterns=DEFAULT_MODEL["files"],
            )

        model_names = [d for d in os.listdir(embeddings_path) if os.path.isdir(os.path.join(embeddings_path, d))]
        return {
            "required": {
                "model_name": (model_names, {"default": model_names[0]}),
                "prompt": ("STRING", {"default": ""}),
                "values": ("LIST", {"default": []}),
                "descriptions": ("LIST", {"default": []}),
            }
        }

    RETURN_TYPES = ("ANY",)
    RETURN_NAMES = ("value",)
    FUNCTION = "process"
    CATEGORY = NEUROCHAIN_UTILS_CAT
    OUTPUT_NODE = True

    def process(
        self,
        model_name: str,
        prompt: str,
        values: list,
        descriptions: list,
    ):
        model_path = os.path.join(folder_paths.models_dir, SIG_EMBEDDINGS_DIR, model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModel.from_pretrained(model_path)

        text_similarity = TextSimilarity(
            texts=descriptions,
            tokenizer=tokenizer,
            model=model,
        )

        indices = text_similarity.ordered_similar_texts(prompt=prompt)
        result = values[indices[0]]
        return (result,)
