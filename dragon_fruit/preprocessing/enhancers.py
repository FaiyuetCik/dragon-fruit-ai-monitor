"""图像增强 — CLAHE、亮度/对比度调整"""

import cv2
import numpy as np


def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple = (8, 8)) -> np.ndarray:
    """CLAHE 自适应直方图均衡化，改善低光图像对比度。
    Args:
        image: BGR 图像 (H, W, 3), uint8
        clip_limit: 对比度剪切阈值
        tile_grid_size: 网格大小
    Returns:
        增强后的 BGR 图像
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def adjust_brightness_contrast(image: np.ndarray, alpha: float = 1.2, beta: float = 10) -> np.ndarray:
    """亮度和对比度调整。
    Args:
        image: BGR 图像, uint8
        alpha: 对比度因子 (>1 增强对比度)
        beta: 亮度增量 (>0 增加亮度)
    Returns:
        调整后的图像
    """
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
