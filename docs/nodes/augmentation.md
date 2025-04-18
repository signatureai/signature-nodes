# Augmentation Nodes

## RandomCropAugmentation

Applies random crop augmentation to images with configurable dimensions and frequency.

This node performs random cropping operations on input images. It allows precise control over the
crop dimensions through minimum and maximum window sizes, target dimensions, and application
probability.

### Inputs

| Group    | Name         | Type           | Default | Extras           |
| -------- | ------------ | -------------- | ------- | ---------------- |
| required | height       | `INT`          | 1024    | min=32, step=32  |
| required | width        | `INT`          | 1024    | min=32, step=32  |
| required | min_window   | `INT`          | 256     | step=32          |
| required | max_window   | `INT`          | 1024    | step=32          |
| required | percent      | `FLOAT`        | 1.0     | min=0.0, max=1.0 |
| optional | augmentation | `AUGMENTATION` | None    |                  |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| augmentation | `AUGMENTATION` |

??? note "Source code"

    ```python
    class RandomCropAugmentation:
        """Applies random crop augmentation to images with configurable dimensions and frequency.

        This node performs random cropping operations on input images. It allows precise control over the
        crop dimensions through minimum and maximum window sizes, target dimensions, and application
        probability.

        Args:
            height (int): Target height for the crop operation. Must be at least 32 and a multiple of 32.
            width (int): Target width for the crop operation. Must be at least 32 and a multiple of 32.
            min_window (int): Minimum size of the crop window. Must be a multiple of 32.
            max_window (int): Maximum size of the crop window. Must be a multiple of 32.
            percent (float): Probability of applying the crop, from 0.0 to 1.0.
            augmentation (AUGMENTATION, optional): Existing augmentation to chain with. Defaults to None.

        Returns:
            tuple: Contains a single element:
                augmentation (AUGMENTATION): The configured crop augmentation operation.

        Raises:
            ValueError: If any dimension parameters are not multiples of 32.
            ValueError: If min_window is larger than max_window.
            ValueError: If percent is not between 0.0 and 1.0.

        Notes:
            - Window size is randomly selected between min_window and max_window for each operation
            - Can be chained with other augmentations through the augmentation parameter
            - All dimension parameters must be multiples of 32 for proper operation
            - Setting percent to 1.0 ensures the crop is always applied
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "height": ("INT", {"default": 1024, "min": 32, "step": 32}),
                    "width": ("INT", {"default": 1024, "min": 32, "step": 32}),
                    "min_window": ("INT", {"default": 256, "step": 32}),
                    "max_window": ("INT", {"default": 1024, "step": 32}),
                    "percent": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0}),
                },
                "optional": {
                    "augmentation": ("AUGMENTATION", {"default": None}),
                },
            }

        RETURN_TYPES = ("AUGMENTATION",)
        FUNCTION = "execute"
        CATEGORY = AUGMENTATION_CAT
        DESCRIPTION = """
        Performs random cropping on images with configurable dimensions and frequency.
        Control crop window size range and target output dimensions.
        Chain with other augmentations for diverse composition variations."""

        def execute(
            self,
            height: int = 1024,
            width: int = 1024,
            min_window: int = 256,
            max_window: int = 1024,
            percent: float = 1.0,
            augmentation: list | None = None,
        ) -> tuple[list]:
            augmentation = random_crop_augmentation(height, width, min_window, max_window, percent, augmentation)

            return (augmentation,)
    ```

## ComposeAugmentation

Combines and applies multiple augmentation operations with consistent random transformations.

This node orchestrates the application of multiple augmentation operations to images and masks. It
provides control over sample generation and reproducibility through seed management.

### Inputs

| Group    | Name         | Type           | Default | Extras                |
| -------- | ------------ | -------------- | ------- | --------------------- |
| required | augmentation | `AUGMENTATION` |         |                       |
| required | samples      | `INT`          | 1       | min=1                 |
| required | seed         | `INT`          |         | max=10000000000000000 |
| optional | image        | `IMAGE`        | None    |                       |
| optional | mask         | `MASK`         | None    |                       |

### Returns

| Name  | Type    |
| ----- | ------- |
| image | `IMAGE` |
| mask  | `MASK`  |

??? note "Source code"

    ```python
    class ComposeAugmentation:
        """Combines and applies multiple augmentation operations with consistent random transformations.

        This node orchestrates the application of multiple augmentation operations to images and masks. It
        provides control over sample generation and reproducibility through seed management.

        Args:
            augmentation (AUGMENTATION): The augmentation operation or chain to apply.
            samples (int): Number of augmented versions to generate. Must be >= 1.
            seed (int): Random seed for reproducible results. Use -1 for random seeding.
                Valid range: -1 to 10000000000000000.
            image (IMAGE, optional): Input image to augment. Defaults to None.
            mask (MASK, optional): Input mask to augment. Defaults to None.

        Returns:
            tuple: Contains two elements:
                images (List[IMAGE]): List of augmented versions of the input image.
                masks (List[MASK]): List of augmented versions of the input mask.

        Raises:
            ValueError: If neither image nor mask is provided.
            ValueError: If samples is less than 1.
            ValueError: If seed is outside valid range.

        Notes:
            - At least one of image or mask must be provided
            - All augmentations are applied consistently to both image and mask
            - Output is always returned as lists, even when samples=1
            - Using a fixed seed ensures reproducible augmentations
            - Supports chaining multiple augmentations through the augmentation parameter
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "augmentation": ("AUGMENTATION",),
                    "samples": ("INT", {"default": 1, "min": 1}),
                    "seed": ("INT", {"default": -1, "min": -1, "max": 10000000000000000}),
                },
                "optional": {
                    "image": ("IMAGE", {"default": None}),
                    "mask": ("MASK", {"default": None}),
                },
            }

        RETURN_TYPES = (
            "IMAGE",
            "MASK",
        )
        FUNCTION = "execute"
        CATEGORY = AUGMENTATION_CAT
        OUTPUT_IS_LIST = (
            True,
            True,
        )
        DESCRIPTION = """
        Applies augmentations to images and masks, creating multiple variations with the same transformations.
        Control the number of samples and use seeds for reproducible results.
        Connect augmentation nodes to create complex transformation chains."""

        def execute(
            self,
            augmentation: list,
            samples: int = 1,
            seed: int = -1,
            image: Optional[torch.Tensor] = None,
            mask: Optional[torch.Tensor] = None,
        ) -> tuple[list, list]:
            # Create a dummy image if only mask is provided
            if image is None and mask is not None:
                image = torch.zeros_like(mask)

            image_tensor = TensorImage.from_BWHC(image) if isinstance(image, torch.Tensor) else None
            mask_tensor = TensorImage.from_BWHC(mask) if isinstance(mask, torch.Tensor) else None

            total_images, total_masks = compose_augmentation(
                augmentation=augmentation,
                samples=samples,
                image_tensor=image_tensor,
                mask_tensor=mask_tensor,
                seed=seed,
            )

            if total_images is None:
                total_images = []
            if total_masks is None:
                total_masks = []
            node_image = [image.get_BWHC() for image in total_images]
            node_mask = [mask.get_BWHC() for mask in total_masks]

            return (
                node_image,
                node_mask,
            )
    ```

## QualityAugmentation

Simulates image quality degradation through compression or downscaling.

This node provides options to reduce image quality in ways that simulate real-world
quality loss scenarios.

### Inputs

| Group    | Name          | Type           | Default     | Extras           |
| -------- | ------------- | -------------- | ----------- | ---------------- |
| required | quality_type  | `LIST`         | compression |                  |
| required | quality_limit | `INT`          | 60          | min=1, max=100   |
| required | percent       | `FLOAT`        | 0.2         | min=0.0, max=1.0 |
| optional | augmentation  | `AUGMENTATION` | None        |                  |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| augmentation | `AUGMENTATION` |

??? note "Source code"

    ```python
    class QualityAugmentation:
        """Simulates image quality degradation through compression or downscaling.

        This node provides options to reduce image quality in ways that simulate real-world
        quality loss scenarios.

        Args:
            quality_type (str): Type of quality reduction:
                - "compression": JPEG-like compression artifacts
                - "downscale": Resolution reduction and upscaling
            quality_limit (int): Quality parameter (1-100, lower = more degradation)
            percent (float): Probability of applying the effect (0.0-1.0)
            augmentation (AUGMENTATION, optional): Existing augmentation to chain with

        Returns:
            tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

        Notes:
            - Compression type simulates JPEG artifacts
            - Downscale type reduces and restores resolution
            - Lower quality limits produce more visible artifacts
            - Can be chained with other augmentations
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "quality_type": (
                        ["compression", "downscale"],
                        {"default": "compression"},
                    ),
                    "quality_limit": ("INT", {"default": 60, "min": 1, "max": 100}),
                    "percent": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0}),
                },
                "optional": {
                    "augmentation": ("AUGMENTATION", {"default": None}),
                },
            }

        RETURN_TYPES = ("AUGMENTATION",)
        FUNCTION = "execute"
        CATEGORY = AUGMENTATION_CAT
        DESCRIPTION = """
        Simulates image quality degradation through compression artifacts or downscaling.
        Control quality reduction level and application frequency.
        Chain with other augmentations for realistic image imperfections."""

        def execute(
            self,
            quality_type: str = "compression",
            quality_limit: int = 60,
            percent: float = 0.2,
            augmentation: Optional[list] = None,
        ) -> tuple[list]:
            augmentation = quality_augmentation(
                quality_type=quality_type,
                quality_limit=quality_limit,
                percent=percent,
                augmentation=augmentation,
            )
            return (augmentation,)
    ```

## DistortionAugmentation

Applies geometric distortion effects to images.

This node provides various types of geometric distortion with configurable severity
and application probability.

### Inputs

| Group    | Name            | Type           | Default | Extras           |
| -------- | --------------- | -------------- | ------- | ---------------- |
| required | distortion_type | `LIST`         | optical |                  |
| required | severity        | `INT`          | 1       | min=1, max=5     |
| required | percent         | `FLOAT`        | 0.3     | min=0.0, max=1.0 |
| optional | augmentation    | `AUGMENTATION` | None    |                  |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| augmentation | `AUGMENTATION` |

??? note "Source code"

    ```python
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
    ```

## GridAugmentation

Applies grid-based transformations to images.

This node provides grid-based image modifications including shuffling and dropout
effects.

### Inputs

| Group    | Name         | Type           | Default | Extras           |
| -------- | ------------ | -------------- | ------- | ---------------- |
| required | grid_type    | `LIST`         | shuffle |                  |
| required | grid_size    | `INT`          | 3       | min=2, max=10    |
| required | percent      | `FLOAT`        | 0.3     | min=0.0, max=1.0 |
| optional | augmentation | `AUGMENTATION` | None    |                  |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| augmentation | `AUGMENTATION` |

??? note "Source code"

    ```python
    class GridAugmentation:
        """Applies grid-based transformations to images.

        This node provides grid-based image modifications including shuffling and dropout
        effects.

        Args:
            grid_type (str): Type of grid transformation:
                - "shuffle": Randomly permute grid cells
                - "dropout": Randomly remove grid cells
            grid_size (int): Number of grid divisions (2-10)
            percent (float): Probability of applying the effect (0.0-1.0)
            augmentation (AUGMENTATION, optional): Existing augmentation to chain with

        Returns:
            tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

        Notes:
            - Image is divided into grid_size x grid_size cells
            - Shuffle randomly reorders grid cells
            - Dropout replaces cells with black
            - Can be chained with other augmentations
            - Maintains overall image structure while adding local variations
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "grid_type": (["shuffle", "dropout"], {"default": "shuffle"}),
                    "grid_size": ("INT", {"default": 3, "min": 2, "max": 10}),
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
        Applies grid-based transformations to images with shuffle or dropout effects.
        Control grid size and application frequency. Maintains overall image structure while adding local variations.
        Chain with other augmentations for creative results."""

        def execute(
            self,
            grid_type: str = "shuffle",
            grid_size: int = 3,
            percent: float = 0.3,
            augmentation: Optional[list] = None,
        ) -> tuple[list]:
            augmentation = grid_augmentation(
                grid_type=grid_type,
                grid_size=grid_size,
                percent=percent,
                augmentation=augmentation,
            )
            return (augmentation,)
    ```

## ShiftScaleAugmentation

Applies random shifting, scaling, and rotation transformations.

This node combines multiple geometric transformations with configurable ranges
and probability.

### Inputs

| Group    | Name         | Type           | Default | Extras           |
| -------- | ------------ | -------------- | ------- | ---------------- |
| required | shift_limit  | `FLOAT`        | 0.1     | min=0.0, max=1.0 |
| required | scale_limit  | `FLOAT`        | 0.2     | min=0.0, max=1.0 |
| required | rotate_limit | `INT`          | 45      | min=0, max=180   |
| required | percent      | `FLOAT`        | 0.3     | min=0.0, max=1.0 |
| optional | augmentation | `AUGMENTATION` | None    |                  |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| augmentation | `AUGMENTATION` |

??? note "Source code"

    ```python
    class ShiftScaleAugmentation:
        """Applies random shifting, scaling, and rotation transformations.

        This node combines multiple geometric transformations with configurable ranges
        and probability.

        Args:
            shift_limit (float): Maximum shift as fraction of image size (0.0-1.0)
            scale_limit (float): Maximum scale factor change (0.0-1.0)
            rotate_limit (int): Maximum rotation angle in degrees (0-180)
            percent (float): Probability of applying transformations (0.0-1.0)
            augmentation (AUGMENTATION, optional): Existing augmentation to chain with

        Returns:
            tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

        Notes:
            - Shift moves image content within frame
            - Scale changes overall image size
            - Rotation angles are randomly sampled
            - Can be chained with other augmentations
            - All transformations are applied together when selected
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "shift_limit": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0}),
                    "scale_limit": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0}),
                    "rotate_limit": ("INT", {"default": 45, "min": 0, "max": 180}),
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
        Applies random shifting, scaling, and rotation transformations to images.
        Control transformation ranges and application frequency.
        Chain with other augmentations for diverse geometric variations."""

        def execute(
            self,
            shift_limit: float = 0.1,
            scale_limit: float = 0.2,
            rotate_limit: int = 45,
            percent: float = 0.3,
            augmentation: Optional[list] = None,
        ) -> tuple[list]:
            augmentation = shift_scale_augmentation(
                shift_limit=shift_limit,
                scale_limit=scale_limit,
                rotate_limit=rotate_limit,
                percent=percent,
                augmentation=augmentation,
            )
            return (augmentation,)
    ```

## BlurAugmentation

Applies various types of blur effects to images.

This node provides multiple blur algorithms with configurable parameters for image
softening effects.

### Inputs

| Group    | Name           | Type           | Default  | Extras           |
| -------- | -------------- | -------------- | -------- | ---------------- |
| required | blur_type      | `LIST`         | gaussian |                  |
| required | blur_limit_min | `INT`          | 3        | min=3, step=3    |
| required | blur_limit_max | `INT`          | 87       | min=3, step=3    |
| required | percent        | `FLOAT`        | 0.3      | min=0.0, max=1.0 |
| optional | augmentation   | `AUGMENTATION` | None     |                  |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| augmentation | `AUGMENTATION` |

??? note "Source code"

    ```python
    class BlurAugmentation:
        """Applies various types of blur effects to images.

        This node provides multiple blur algorithms with configurable parameters for image
        softening effects.

        Args:
            blur_type (str): Type of blur to apply:
                - "gaussian": Gaussian blur
                - "motion": Motion blur
                - "median": Median filter blur
            blur_limit_min (int): Minimum blur kernel size (must be multiple of 3)
            blur_limit_max (int): Maximum blur kernel size (must be multiple of 3)
            percent (float): Probability of applying the blur (0.0-1.0)
            augmentation (AUGMENTATION, optional): Existing augmentation to chain with

        Returns:
            tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

        Notes:
            - Kernel size is randomly selected between min and max limits
            - Different blur types produce distinct softening effects
            - Larger kernel sizes create stronger blur effects
            - Can be chained with other augmentations
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "blur_type": (
                        ["gaussian", "motion", "median"],
                        {"default": "gaussian"},
                    ),
                    "blur_limit_min": ("INT", {"default": 3, "min": 3, "step": 3}),
                    "blur_limit_max": ("INT", {"default": 87, "min": 3, "step": 3}),
                    "percent": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0}),
                },
                "optional": {
                    "augmentation": ("AUGMENTATION", {"default": None}),
                },
            }

        RETURN_TYPES = ("AUGMENTATION",)
        FUNCTION = "execute"
        CATEGORY = AUGMENTATION_CAT
        DESCRIPTION = """Adds blur effects to images with gaussian, motion, or median styles.
        Control blur strength and application frequency. Chain with other augmentations for creative transformations."""

        def execute(
            self,
            blur_type: str = "gaussian",
            blur_limit_min: int = 3,
            blur_limit_max: int = 87,
            percent: float = 0.3,
            augmentation: Optional[list] = None,
        ) -> tuple[list]:
            blur_limit = (blur_limit_min, blur_limit_max)
            augmentation = blur_augmentation(
                blur_type=blur_type,
                blur_limit=blur_limit,
                percent=percent,
                augmentation=augmentation,
            )
            return (augmentation,)
    ```

## BrightnessContrastAugmentation

Applies brightness and contrast adjustments to images.

This node provides controls for adjusting image brightness and contrast with configurable
limits and probability of application.

### Inputs

| Group    | Name             | Type           | Default | Extras           |
| -------- | ---------------- | -------------- | ------- | ---------------- |
| required | brightness_limit | `FLOAT`        | 0.2     | min=0.0, max=1.0 |
| required | contrast_limit   | `FLOAT`        | 0.2     | min=0.0, max=1.0 |
| required | percent          | `FLOAT`        | 0.5     | min=0.0, max=1.0 |
| optional | augmentation     | `AUGMENTATION` | None    |                  |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| augmentation | `AUGMENTATION` |

??? note "Source code"

    ```python
    class BrightnessContrastAugmentation:
        """Applies brightness and contrast adjustments to images.

        This node provides controls for adjusting image brightness and contrast with configurable
        limits and probability of application.

        Args:
            brightness_limit (float): Maximum brightness adjustment range (0.0-1.0)
            contrast_limit (float): Maximum contrast adjustment range (0.0-1.0)
            percent (float): Probability of applying the augmentation (0.0-1.0)
            augmentation (AUGMENTATION, optional): Existing augmentation to chain with

        Returns:
            tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

        Notes:
            - Brightness adjustments are applied as multiplicative factors
            - Contrast adjustments modify image histogram spread
            - Can be chained with other augmentations
            - Actual adjustment values are randomly sampled within limits
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "brightness_limit": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0}),
                    "contrast_limit": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0}),
                    "percent": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
                },
                "optional": {
                    "augmentation": ("AUGMENTATION", {"default": None}),
                },
            }

        RETURN_TYPES = ("AUGMENTATION",)
        FUNCTION = "execute"
        CATEGORY = AUGMENTATION_CAT
        DESCRIPTION = """Adjusts image brightness and contrast during generation.
        Control modification ranges and application frequency.
        Chain with other augmentations for creative image variations."""

        def execute(
            self,
            brightness_limit: float = 0.2,
            contrast_limit: float = 0.2,
            percent: float = 0.5,
            augmentation: Optional[list] = None,
        ) -> tuple[list]:
            augmentation = brightness_contrast_augmentation(
                brightness_limit=brightness_limit,
                contrast_limit=contrast_limit,
                percent=percent,
                augmentation=augmentation,
            )
            return (augmentation,)
    ```

## PerspectiveAugmentation

Applies perspective transformation effects to images.

This node creates perspective distortion effects that simulate viewing angle changes,
with configurable strength and probability.

### Inputs

| Group    | Name         | Type           | Default | Extras            |
| -------- | ------------ | -------------- | ------- | ----------------- |
| required | scale        | `FLOAT`        | 0.05    | min=0.01, max=0.5 |
| required | keep_size    | `BOOLEAN`      | True    |                   |
| required | percent      | `FLOAT`        | 0.3     | min=0.0, max=1.0  |
| optional | augmentation | `AUGMENTATION` | None    |                   |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| augmentation | `AUGMENTATION` |

??? note "Source code"

    ```python
    class PerspectiveAugmentation:
        """Applies perspective transformation effects to images.

        This node creates perspective distortion effects that simulate viewing angle changes,
        with configurable strength and probability.

        Args:
            scale (float): Strength of perspective effect (0.01-0.5)
            keep_size (bool): Whether to maintain original image size
            percent (float): Probability of applying the effect (0.0-1.0)
            augmentation (AUGMENTATION, optional): Existing augmentation to chain with

        Returns:
            tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

        Notes:
            - Scale controls the intensity of perspective change
            - keep_size=True maintains original dimensions
            - keep_size=False may change image size
            - Can be chained with other augmentations
            - Simulates realistic viewing angle variations
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "scale": ("FLOAT", {"default": 0.05, "min": 0.01, "max": 0.5}),
                    "keep_size": ("BOOLEAN", {"default": True}),
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
        Applies perspective transformations to images, simulating viewing angle changes.
        Control effect strength and application frequency.
        Chain with other augmentations for realistic spatial variations."""

        def execute(
            self,
            scale: float = 0.05,
            keep_size: bool = True,
            percent: float = 0.3,
            augmentation: Optional[list] = None,
        ) -> tuple[list]:
            augmentation = perspective_augmentation(
                scale=scale, keep_size=keep_size, percent=percent, augmentation=augmentation
            )
            return (augmentation,)
    ```

## FlipAugmentation

Applies horizontal or vertical flip augmentation to images with configurable probability.

This node performs random flip transformations on input images. It supports both horizontal and
vertical flip operations with adjustable probability of application.

### Inputs

| Group    | Name         | Type           | Default    | Extras           |
| -------- | ------------ | -------------- | ---------- | ---------------- |
| required | flip         | `LIST`         | horizontal |                  |
| required | percent      | `FLOAT`        | 0.5        | min=0.0, max=1.0 |
| optional | augmentation | `AUGMENTATION` | None       |                  |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| augmentation | `AUGMENTATION` |

??? note "Source code"

    ```python
    class FlipAugmentation:
        """Applies horizontal or vertical flip augmentation to images with configurable probability.

        This node performs random flip transformations on input images. It supports both horizontal and
        vertical flip operations with adjustable probability of application.

        Args:
            flip (str): Direction of flip operation, either:
                - "horizontal": Flips image left to right
                - "vertical": Flips image top to bottom
            percent (float): Probability of applying the flip, from 0.0 to 1.0.
            augmentation (AUGMENTATION, optional): Existing augmentation to chain with. Defaults to None.

        Returns:
            tuple: Contains a single element:
                augmentation (AUGMENTATION): The configured flip augmentation operation.

        Raises:
            ValueError: If flip direction is not "horizontal" or "vertical".
            ValueError: If percent is not between 0.0 and 1.0.

        Notes:
            - Flip direction cannot be changed after initialization
            - Setting percent to 0.5 applies the flip to approximately half of all samples
            - Can be chained with other augmentations through the augmentation parameter
            - Transformations are applied consistently when used with ComposeAugmentation
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "flip": (["horizontal", "vertical"], {"default": "horizontal"}),
                    "percent": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
                },
                "optional": {
                    "augmentation": ("AUGMENTATION", {"default": None}),
                },
            }

        RETURN_TYPES = ("AUGMENTATION",)
        FUNCTION = "execute"
        CATEGORY = AUGMENTATION_CAT
        DESCRIPTION = """
        Applies horizontal or vertical flip transformations to images with adjustable probability.
        Creates mirror-image variations of your content.
        Chain with other augmentations for diverse image transformations."""

        def execute(
            self,
            flip: str = "horizontal",
            percent: float = 0.5,
            augmentation: Optional[list] = None,
        ) -> tuple[list]:
            augmentation = flip_augmentation(flip, percent, augmentation)
            return (augmentation,)
    ```

## RotationAugmentation

Rotates images by random angles within specified limits.

This node performs random rotation augmentation with configurable angle limits and
application probability.

### Inputs

| Group    | Name         | Type           | Default | Extras           |
| -------- | ------------ | -------------- | ------- | ---------------- |
| required | limit        | `INT`          | 45      | min=0, max=180   |
| required | percent      | `FLOAT`        | 0.5     | min=0.0, max=1.0 |
| optional | augmentation | `AUGMENTATION` | None    |                  |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| augmentation | `AUGMENTATION` |

??? note "Source code"

    ```python
    class RotationAugmentation:
        """Rotates images by random angles within specified limits.

        This node performs random rotation augmentation with configurable angle limits and
        application probability.

        Args:
            limit (int): Maximum rotation angle in degrees (0-180)
            percent (float): Probability of applying the rotation (0.0-1.0)
            augmentation (AUGMENTATION, optional): Existing augmentation to chain with

        Returns:
            tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

        Notes:
            - Rotation angles are randomly sampled between -limit and +limit
            - Empty areas after rotation are filled with black
            - Can be chained with other augmentations
            - Original aspect ratio is preserved
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "limit": ("INT", {"default": 45, "min": 0, "max": 180}),
                    "percent": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
                },
                "optional": {
                    "augmentation": ("AUGMENTATION", {"default": None}),
                },
            }

        RETURN_TYPES = ("AUGMENTATION",)
        FUNCTION = "execute"
        CATEGORY = AUGMENTATION_CAT
        DESCRIPTION = """
        Rotates images by random angles within specified limits.
        Control rotation angle range and application frequency.
        Chain with other augmentations for diverse orientation variations."""

        def execute(
            self,
            limit: int = 45,
            percent: float = 0.5,
            augmentation: Optional[list] = None,
        ) -> tuple[list]:
            augmentation = rotation_augmentation(limit=limit, percent=percent, augmentation=augmentation)
            return (augmentation,)
    ```

## CutoutAugmentation

Creates random rectangular cutouts in images.

This node randomly removes rectangular regions from images by filling them with black,
useful for regularization and robustness training.

### Inputs

| Group    | Name          | Type           | Default | Extras           |
| -------- | ------------- | -------------- | ------- | ---------------- |
| required | num_holes     | `INT`          | 8       | min=1, max=20    |
| required | max_size      | `INT`          | 30      | min=1, max=100   |
| required | percent       | `FLOAT`        | 0.3     | min=0.0, max=1.0 |
| optional | min_num_holes | `INT`          | 1       | min=1, max=20    |
| optional | min_size      | `INT`          | 1       | min=1, max=100   |
| optional | augmentation  | `AUGMENTATION` | None    |                  |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| augmentation | `AUGMENTATION` |

??? note "Source code"

    ```python
    class CutoutAugmentation:
        """Creates random rectangular cutouts in images.

        This node randomly removes rectangular regions from images by filling them with black,
        useful for regularization and robustness training.

        Args:
            num_holes (int): Number of cutout regions to create (1-20)
            max_size (int): Maximum size of cutout regions in pixels (1-100)
            percent (float): Probability of applying cutouts (0.0-1.0)
            augmentation (AUGMENTATION, optional): Existing augmentation to chain with

        Returns:
            tuple[AUGMENTATION]: Single-element tuple containing the configured augmentation

        Notes:
            - Cutout positions are randomly selected
            - Each cutout region is independently sized
            - Regions are filled with black (zero) values
            - Can be chained with other augmentations
            - Useful for preventing overfitting
        """

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "num_holes": ("INT", {"default": 8, "min": 1, "max": 20}),
                    "max_size": ("INT", {"default": 30, "min": 1, "max": 100}),
                    "percent": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0}),
                },
                "optional": {
                    "min_num_holes": ("INT", {"default": 1, "min": 1, "max": 20}),
                    "min_size": ("INT", {"default": 1, "min": 1, "max": 100}),
                    "augmentation": ("AUGMENTATION", {"default": None}),
                },
            }

        RETURN_TYPES = ("AUGMENTATION",)
        FUNCTION = "execute"
        CATEGORY = AUGMENTATION_CAT
        DESCRIPTION = """Creates random black rectangular cutouts in images.
        Control number, size, and frequency of cutouts.
        Useful for regularization and preventing overfitting.
        Chain with other augmentations for creative effects."""

        def execute(
            self,
            num_holes: int = 8,
            max_size: int = 30,
            percent: float = 0.3,
            min_num_holes: int = 1,
            min_size: int = 1,
            augmentation: Optional[list] = None,
        ) -> tuple[list]:
            augmentation = cutout_augmentation(
                num_holes=num_holes,
                max_size=max_size,
                percent=percent,
                min_num_holes=min_num_holes,
                min_size=min_size,
                augmentation=augmentation,
            )
            return (augmentation,)

    ```
