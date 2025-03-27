import random
from typing import Tuple

import cv2
import numpy as np
import torch


class GuidedRandomCrop:
    """Node that performs random cropping guided by masks"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),  # List/Batch of images
                "masks": ("MASK",),  # List/Batch of masks
                "output_width": ("INT", {"default": 256, "min": 32, "max": 2048}),
                "output_height": ("INT", {"default": 256, "min": 32, "max": 2048}),
                "min_crop_size": ("INT", {"default": 128, "min": 32, "max": 2048}),
                "max_crop_size": ("INT", {"default": 256, "min": 32, "max": 2048}),
                "num_samples": ("INT", {"default": 4, "min": 1, "max": 200}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("crops", "debug_view")
    FUNCTION = "guided_crop"
    CATEGORY = "image/processing"
    DESCRIPTION = """Takes images and corresponding masks as input. The node identifies areas where the mask is present
    and randomly samples points within those areas.
    For each sampled point, it creates a crop of specified width and height,
    adjusting the crop window position if needed to stay within image boundaries. Returns both the crops and a debug
    visualization showing the mask area (blue hatched pattern), sampled points (red dots), and crop windows (blue
    rectangles).
    """

    def guided_crop(
        self,
        images: torch.Tensor,
        masks: torch.Tensor,
        output_width: int = 256,
        output_height: int = 256,
        min_crop_size: int = 128,
        max_crop_size: int = 256,
        num_samples: int = 4,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Perform guided random cropping based on masks
        """
        # Convert tensors to numpy for easier processing
        images_np = images.cpu().numpy()
        masks_np = masks.cpu().numpy()

        batch_size = images_np.shape[0]
        crops = []
        debug_views = []

        for b in range(batch_size):
            image = images_np[b]
            mask = masks_np[b]

            # Find valid points inside the mask where the mask is greater than 0.5
            valid_points = np.where(mask > 0.5)
            # If there are no valid points on y-coordinates, skip this image
            if len(valid_points[0]) == 0:
                continue

            point_indices = random.sample(range(len(valid_points[0])), min(num_samples, len(valid_points[0])))

            debug_view = image.copy()

            # Add semi-transparent mask overlay
            mask_overlay = np.zeros_like(image)
            mask_overlay[mask > 0.5] = [0, 1, 1]
            debug_view = cv2.addWeighted(debug_view, 1, mask_overlay, 0.3, 0)

            for idx in point_indices:
                y, x = valid_points[0][idx], valid_points[1][idx]
                # Randomly select crop dimensions between min and max
                crop_size = random.randint(min_crop_size, max_crop_size)

                # Calculate initial crop boundaries
                half_w = crop_size // 2
                half_h = crop_size // 2

                # Calculate initial boundaries
                start_x = x - half_w
                end_x = x + half_w
                start_y = y - half_h
                end_y = y + half_h

                # Shift the box if it goes out of bounds
                if start_x < 0:
                    # Shift right
                    end_x -= start_x  # Add the negative offset
                    start_x = 0
                elif end_x > image.shape[1]:
                    # Shift left
                    offset = end_x - image.shape[1]
                    end_x = image.shape[1]
                    start_x -= offset

                if start_y < 0:
                    # Shift down
                    end_y -= start_y  # Add the negative offset
                    start_y = 0
                elif end_y > image.shape[0]:
                    # Shift up
                    offset = end_y - image.shape[0]
                    end_y = image.shape[0]
                    start_y -= offset

                # Get the crop
                crop = image[start_y:end_y, start_x:end_x]

                # Resize the crop to match output dimensions
                standardized_crop = cv2.resize(crop, (output_width, output_height), interpolation=cv2.INTER_LINEAR)

                # Append the standardized crop
                crops.append(standardized_crop)

                # Draw debug visualization
                cv2.rectangle(debug_view, (start_x, start_y), (end_x, end_y), (0, 0, 1), 2)  # Blue rectangle
                cv2.circle(debug_view, (x, y), 5, (1, 0, 0), -1)  # Red point

            debug_views.append(debug_view)

        # Convert lists to tensors
        crops_tensor = torch.from_numpy(np.stack(crops)).to(images.device)
        debug_views_tensor = torch.from_numpy(np.stack(debug_views)).to(images.device)

        return (crops_tensor, debug_views_tensor)
