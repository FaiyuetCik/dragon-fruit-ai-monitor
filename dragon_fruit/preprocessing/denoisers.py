"""图像降噪 — 高斯模糊、非局部均值降噪"""

import cv2
import numpy as np


def denoise_gaussian(image: np.ndarray, kernel_size: tuple = (5, 5)) -> np.ndarray:
    """高斯模糊降噪（速度快，适合实时场景）。
    Args:
        image: BGR 图像, uint8
        kernel_size: 高斯核大小，必须为奇数
    Returns:
        降噪后的图像
    """
    return cv2.GaussianBlur(image, kernel_size, 0)


def denoise_nlm(image: np.ndarray, h: float = 10, h_color: float = 10,
                template_size: int = 7, search_size: int = 21) -> np.ndarray:
    """非局部均值降噪（效果好，适合离线高质量处理）。
    Args:
        image: BGR 图像, uint8
        h: 亮度滤波强度
        h_color: 色彩滤波强度
        template_size: 模板窗口大小
        search_size: 搜索窗口大小
    Returns:
        降噪后的图像
    """
    return cv2.fastNlMeansDenoisingColored(image, None, h, h_color, template_size, search_size)


def denoise_fast(image: np.ndarray) -> np.ndarray:
    """快速降噪，适合大多数场景。"""
    return denoise_gaussian(image, kernel_size=(3, 3))
