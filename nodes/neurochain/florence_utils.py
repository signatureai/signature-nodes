from abc import ABC, abstractmethod
from typing import Optional

import torch
from signature_core.img.tensor_image import TensorImage

from .utils import create_bbox_mask, draw_polygons, overlay_bboxes


class FlorenceTaskProcessor(ABC):
    accepts_text_prompt = False
    task_tokens: list

    @abstractmethod
    def process_output(
        self, input_img: torch.Tensor, text_prompt: str, raw_output
    ) -> tuple[Optional[torch.Tensor], Optional[torch.Tensor], str]:
        raise NotImplementedError


class CaptionProcessor(FlorenceTaskProcessor):
    task_tokens: list = [
        "<CAPTION>",
        "<DETAILED_CAPTION>",
        "<MORE_DETAILED_CAPTION>",
        "<OCR>",
    ]

    def process_output(
        self, input_img: torch.Tensor, text_prompt: str, raw_output
    ) -> tuple[Optional[torch.Tensor], Optional[torch.Tensor], str]:
        placeholder_img = torch.zeros(1, 512, 512)
        return placeholder_img, placeholder_img, raw_output


class TextGuidedObjectDetectProcessor(FlorenceTaskProcessor):
    accepts_text_prompt = True
    task_tokens: list = [
        "<OPEN_VOCABULARY_DETECTION>",
        "<CAPTION_TO_PHRASE_GROUNDING>",
        "<OCR_WITH_REGION>",
    ]

    def process_output(
        self, input_img: torch.Tensor, text_prompt: str, raw_output
    ) -> tuple[Optional[torch.Tensor], Optional[torch.Tensor], str]:
        label_keys = ["bboxes_labels", "labels"]
        labels = None
        for label_key in label_keys:
            if label_key in raw_output:
                labels = raw_output[label_key]

        bboxes_keys = ["bboxes", "quad_boxes"]
        bboxes = None
        for bboxes_key in bboxes_keys:
            if bboxes_key in raw_output:
                bboxes = raw_output[bboxes_key]

        img_np = TensorImage.from_BWHC(input_img).get_numpy_image()
        overlayed_img = overlay_bboxes(img_np=img_np, bboxes=bboxes, labels=labels)
        bbox_mask = create_bbox_mask(img_np=img_np, bboxes=bboxes)

        overlayed_img = TensorImage.from_numpy(overlayed_img).get_BWHC()
        bbox_mask = TensorImage.from_numpy(bbox_mask).get_BWHC()
        return overlayed_img, bbox_mask, raw_output


class TextGuidedSegmentationProcessor(FlorenceTaskProcessor):
    accepts_text_prompt = True
    task_tokens: list = ["<REFERRING_EXPRESSION_SEGMENTATION>"]

    def process_output(
        self, input_img: torch.Tensor, text_prompt: str, raw_output
    ) -> tuple[Optional[torch.Tensor], Optional[torch.Tensor], str]:
        img_np = TensorImage.from_BWHC(input_img).get_numpy_image()

        overlayed_img = draw_polygons(
            image=img_np, prediction=raw_output, is_bin_mask=False, fill_mask=True
        )
        seg_mask = draw_polygons(
            image=img_np, prediction=raw_output, is_bin_mask=True, fill_mask=True
        )

        overlayed_img = TensorImage.from_numpy(overlayed_img).get_BWHC()
        seg_mask = TensorImage.from_numpy(seg_mask).get_BWHC()

        return overlayed_img, seg_mask, raw_output


class ObjectDetectProcessor(TextGuidedObjectDetectProcessor):
    accepts_text_prompt = False
    task_tokens: list = ["<OD>", "<DENSE_REGION_CAPTION>", "<REGION_PROPOSAL>"]


FLORENCE_PROCESSORS = [
    CaptionProcessor(),
    TextGuidedObjectDetectProcessor(),
    ObjectDetectProcessor(),
    TextGuidedSegmentationProcessor(),
]
