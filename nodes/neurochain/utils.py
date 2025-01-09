import json
import os
import random
import time
import urllib

import cv2
import numpy as np
import sagemaker
from botocore.exceptions import ClientError

BASE_COMFY_DIR = os.path.dirname(os.path.realpath(__file__)).split("custom_nodes")[0]
COMFY_IMAGES_DIR = os.path.join(BASE_COMFY_DIR, "input")


# Hack: string type that is always equal in not equal comparisons
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False


# Our any instance wants to be a wildcard string
WILDCARD = AnyType("*")


def get_async_output(output_location, wait_interval: float = 0.5, timeout: int = 20):
    sagemaker_session = sagemaker.session.Session()
    count = 0
    output_url = urllib.parse.urlparse(output_location)
    bucket = output_url.netloc
    key = output_url.path[1:]
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError("Timed out waiting for output")
        try:
            return sagemaker_session.read_s3_file(bucket=bucket, key_prefix=key)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                print("waiting for output...")
                time.sleep(wait_interval)
                count += 1
                continue
            print(count)
            raise


def overlay_bboxes(img_np, bboxes, labels: list | None = None):
    image_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    for idx, bbox in enumerate(bboxes):

        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(image_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if labels is not None:
            label = labels[idx]
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            label_w, label_h = label_size
            cv2.rectangle(image_bgr, (x1, y1 - label_h - 10), (x1 + label_w, y1), (0, 255, 0), -1)
            cv2.putText(image_bgr, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    return image_rgb


def create_bbox_mask(img_np, bboxes):
    image_shape = img_np.shape
    if len(image_shape) == 3:
        H, W, _ = image_shape
    else:
        H, W = image_shape

    # Initialize an empty mask
    mask = np.zeros((H, W), dtype=np.uint8)

    # Fill in the mask for each bounding box
    for bbox in bboxes:
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)  # -1 means fill the rectangle

    return mask


def draw_polygons(image, prediction, is_bin_mask=False, fill_mask=False):
    """
    Draws segmentation masks with polygons on an image using OpenCV.

    Parameters:
    - image: OpenCV image (numpy array)
    - prediction: Dictionary containing 'polygons' and 'labels' keys.
                  'polygons' is a list of lists, each containing vertices of a polygon.
                  'labels' is a list of labels corresponding to each polygon.
    - fill_mask: Boolean indicating whether to fill the polygons with color.
    """
    image_shape = image.shape
    if len(image_shape) == 3:
        H, W, _ = image_shape
    else:
        H, W = image_shape

    if is_bin_mask:
        image = np.zeros((H, W), dtype=np.uint8)

    # Set up scale factor if needed (use 1 if not scaling)
    scale = 1

    # Define a colormap (you may want to customize this)
    colormap = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(100)]

    # Create an overlay for transparency
    overlay = image.copy()

    # Iterate over polygons and labels
    for polygons, label in zip(prediction["polygons"], prediction["labels"]):

        color = 255 if is_bin_mask else (0, 255, 255)

        for _polygon in polygons:
            _polygon = np.array(_polygon).reshape((-1, 1, 2))
            if len(_polygon) < 3:
                print("Invalid polygon:", _polygon)
                continue

            _polygon = (_polygon * scale).astype(np.int32)

            if is_bin_mask:
                cv2.fillPoly(image, [_polygon], color)
            else:
                # Draw the polygon
                if fill_mask:
                    cv2.fillPoly(overlay, [_polygon], color)
                cv2.polylines(overlay, [_polygon], True, color, 1)
                cv2.polylines(image, [_polygon], True, color, 1)

                # # Draw the label text
                # text_position = (_polygon[0][0][0] + 8, _polygon[0][0][1] + 2)
                # cv2.putText(overlay, label, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    if not is_bin_mask:
        # Apply the overlay with transparency
        cv2.addWeighted(overlay, 0.002, image, 0.998, 0, image)
    return image


def get_secret(session, secret_name, region_name="eu-west-1"):
    client = session.client(service_name="secretsmanager", region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            return json.loads(response["SecretString"])
    except Exception as e:
        print(f"Error getting secret: {e}")
        raise
