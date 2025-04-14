from typing import Optional

from signature_core.functional.augmentation import distortion_augmentation

from ...categories import AUGMENTATION_CAT


class DistortionAugmentation:
    """Applies geometric distortion effects to images.

    This node provides various types of geometric distortion with configurable severity
    and application probability.

    Args:
        distortion_type (str): Type of distortion to apply:
            - "optical": Lens-like distortion
            - "grid": Grid-based warping
            - "elastic": Elastic deformation
        severity (int): Intensity of the distortion effect (1-5)
        percent (float): Probability of applying the effect (0.0-1.0)
        augmentation (AUGMENTATION, optional): Existing augmentation to chain with

    Returns:
        tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

    Notes:
        - Each distortion type produces unique geometric deformations
        - Higher severity values create stronger distortion effects
        - Can be chained with other augmentations
        - Maintains overall image structure while adding local deformations
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "distortion_type": (
                    ["optical", "grid", "elastic"],
                    {"default": "optical"},
                ),
                "severity": ("INT", {"default": 1, "min": 1, "max": 5}),
                "percent": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                "augmentation": ("AUGMENTATION", {"default": None}),
            },
        }

    RETURN_TYPES = ("AUGMENTATION",)
    FUNCTION = "execute"
    CATEGORY = AUGMENTATION_CAT
    DESCRIPTION = """
    Applies geometric distortion effects to images with optical, grid, or elastic deformations.
    Control distortion intensity and application frequency.
    Chain with other augmentations for complex transformations."""

    def execute(
        self,
        distortion_type: str = "optical",
        severity: int = 1,
        percent: float = 0.3,
        augmentation: Optional[list] = None,
    ) -> tuple[list]:
        augmentation = distortion_augmentation(
            distortion_type=distortion_type,
            severity=severity,
            percent=percent,
            augmentation=augmentation,
        )
        return (augmentation,)
