"""几何分析 — 边缘检测、倾斜角度计算"""

import cv2
import numpy as np
import math


def detect_tilt_angle(image: np.ndarray) -> float:
    """检测植株倾斜角度（基于 Hough 线检测）。
    Args:
        image: BGR 图像 (H, W, 3), uint8
    Returns:
        倾斜角度（度），0=垂直，正值=顺时针偏离
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                            minLineLength=80, maxLineGap=20)
    if lines is None or len(lines) == 0:
        return 0.0

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = math.degrees(math.atan2(x2 - x1, y2 - y1))
        angles.append(abs(angle))

    if not angles:
        return 0.0

    # 使用中位数减少噪声线的影响
    return float(np.median(angles))


def estimate_plant_coverage(image: np.ndarray,
                            green_mask: np.ndarray = None) -> float:
    """估算植株覆盖比例：前景绿色区域占画面比例。
    Args:
        image: BGR 图像
        green_mask: 可选的绿色掩码；若为 None 则自动计算
    Returns:
        覆盖比例 0.0-1.0
    """
    if green_mask is None:
        from dragon_fruit.growth.color_analysis import segment_foliage
        green_mask = segment_foliage(image)

    total_pixels = image.shape[0] * image.shape[1]
    if total_pixels == 0:
        return 0.0
    return float(np.count_nonzero(green_mask)) / total_pixels
