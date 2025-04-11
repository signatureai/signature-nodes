import torch
from signature_core.img.tensor_image import TensorImage


def image_array_to_tensor(x: TensorImage):
    image = x.get_BWHC()
    mask = torch.ones((x.shape[0], x.shape[2], x.shape[3], 1), dtype=torch.float32)

    if x.shape[-1] == 4:
        mask = image[:, :, :, -1]

    return (
        image,
        mask,
    )
