import os

import comfy.model_management  # type: ignore
import folder_paths  # type: ignore
from neurochain.agents.audio.audio_transcriber import AudioTranscriber

from ....categories import AUDIO_CAT

SIG_MODELS_DIR = "sig_models"


class TranscribeAudio:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("transcript",)
    FUNCTION = "process"
    CATEGORY = AUDIO_CAT
    OUTPUT_NODE = True

    def process(self, audio: dict):
        base_model_path = os.path.join(folder_paths.models_dir, SIG_MODELS_DIR)
        if not os.path.exists(base_model_path):
            os.makedirs(base_model_path)

        device = comfy.model_management.get_torch_device()
        transcriber = AudioTranscriber(base_model_path, device)

        audio_tensor = audio["waveform"]
        sample_rate = audio["sample_rate"]
        transcript = transcriber.transcribe(audio_tensor, sample_rate)

        return (transcript,)
