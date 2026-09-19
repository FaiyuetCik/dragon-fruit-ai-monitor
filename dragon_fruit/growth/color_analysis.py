"""HSV 颜色空间分析 — 绿化指数、黄化检测"""

import cv2
import numpy as np


# HSV 绿色范围（色相约 35-85）
GREEN_LOWER = np.array([35, 40, 40])
GREEN_UPPER = np.array([85, 255, 255])

# HSV 黄色/枯黄范围（色相约 20-35）
YELLOW_LOWER = np.array([20, 40, 40])
YELLOW_UPPER = np.array([35, 255, 255])

# HSV 红色/紫色范围（火龙果果实剔除）
RED_LOWER_1 = np.array([0, 40, 40])
RED_UPPER_1 = np.array([10, 255, 255])
RED_LOWER_2 = np.array([160, 40, 40])
RED_UPPER_2 = np.array([180, 255, 255])


def compute_greenness_index(image: np.ndarray) -> float:
    """计算绿化指数：绿色像素占总像素的比例。
    Args:
        image: BGR 图像 (H, W, 3), uint8
    Returns:
        绿化指数 0.0-1.0
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)
    total_pixels = image.shape[0] * image.shape[1]
    if total_pixels == 0:
        return 0.0
    return float(np.count_nonzero(mask)) / total_pixels


def compute_yellowness_ratio(image: np.ndarray) -> float:
    """计算黄化率：黄色像素在非果实区域中的占比。
    Args:
        image: BGR 图像 (H, W, 3), uint8
    Returns:
        黄化率 0.0-1.0
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    yellow_mask = cv2.inRange(hsv, YELLOW_LOWER, YELLOW_UPPER)
    red_mask1 = cv2.inRange(hsv, RED_LOWER_1, RED_UPPER_1)
    red_mask2 = cv2.inRange(hsv, RED_LOWER_2, RED_UPPER_2)
    fruit_mask = cv2.bitwise_or(red_mask1, red_mask2)

    yellow_pixels = np.count_nonzero(yellow_mask)
    total_non_fruit = np.count_nonzero(cv2.bitwise_not(fruit_mask))

    if total_non_fruit == 0:
        return 0.0
    return float(yellow_pixels) / total_non_fruit


def segment_foliage(image: np.ndarray) -> np.ndarray:
    """HSV 阈值法分割植株前景（绿色叶片+茎干区域）。
    Args:
        image: BGR 图像 (H, W, 3), uint8
    Returns:
        二值掩码 (H, W), uint8, 255=前景
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    return green_mask
