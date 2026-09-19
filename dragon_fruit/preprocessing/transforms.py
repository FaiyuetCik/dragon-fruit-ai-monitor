"""图像变换 — letterbox 尺寸调整、归一化、张量转换"""

import cv2
import numpy as np
import torch

from utils.augmentations import letterbox


def resize_letterbox(image: np.ndarray, target_size: tuple = (640, 640),
                     stride: int = 32, auto: bool = True) -> np.ndarray:
    """使用 YOLOv5 letterbox 调整图像尺寸，保持宽高比并填充。
    Args:
        image: BGR 图像 (H, W, 3), uint8
        target_size: 目标尺寸 (height, width)
        stride: 步长约束
        auto: 自动最小填充
    Returns:
        调整后的图像 (target_h, target_w, 3)
    """
    return letterbox(image, target_size, stride=stride, auto=auto)[0]


def to_tensor(image: np.ndarray) -> torch.Tensor:
    """BGR HWC uint8 → RGB CHW float32 [0, 1]。
    Args:
        image: BGR 图像 (H, W, 3), uint8
    Returns:
        tensor (1, 3, H, W), float32, 0.0-1.0
    """
    im = image.transpose((2, 0, 1))[::-1]  # HWC→CHW, BGR→RGB
    im = np.ascontiguousarray(im)
    im = torch.from_numpy(im).float() / 255.0
    if im.ndimension() == 3:
        im = im.unsqueeze(0)
    return im
