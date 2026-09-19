"""生长异常检测编排器"""

import numpy as np

from dragon_fruit.config import MonitoringConfig
from dragon_fruit.growth.color_analysis import (
    compute_greenness_index,
    compute_yellowness_ratio,
)
from dragon_fruit.growth.geometry import detect_tilt_angle


class GrowthAnomalyDetector:
    """生长异常检测器 — 纯经典 CV（HSV + 边缘检测），无需深度学习。"""

    def __init__(self, config: MonitoringConfig):
        self.greenness_threshold = config.greenness_threshold
        self.yellowness_threshold = config.yellowness_threshold
        self.tilt_threshold = config.tilt_threshold

    def analyze(self, image: np.ndarray) -> dict:
        """对输入图像运行全部生长异常分析。
        Args:
            image: BGR 图像 (H, W, 3), uint8
        Returns:
            异常分析结果字典
        """
        greenness = compute_greenness_index(image)
        yellowness = compute_yellowness_ratio(image)
        tilt_angle = detect_tilt_angle(image)

        anomalies = []
        recommendations = []

        # Greenness evaluation
        if greenness < self.greenness_threshold:
            greenness_status = "low"
            anomalies.append("insufficient_greenery")
            recommendations.append("Low greenery coverage. Check soil nutrients and irrigation.")
        else:
            greenness_status = "normal"

        # Yellowness evaluation
        yellowness_alert = yellowness > self.yellowness_threshold
        if yellowness_alert:
            anomalies.append("leaf_yellowing")
            recommendations.append("Leaf yellowing detected. Check: N/Fe deficiency, overwatering, or early disease.")

        # Tilt evaluation
        tilt_alert = tilt_angle > self.tilt_threshold
        if tilt_alert:
            anomalies.append("plant_tilting")
            recommendations.append(f"Plant tilted {tilt_angle:.1f} deg. Check support structure and root health.")

        return {
            "greenness_index": round(greenness, 4),
            "greenness_status": greenness_status,
            "yellowness_ratio": round(yellowness, 4),
            "yellowness_alert": yellowness_alert,
            "tilt_angle_degrees": round(tilt_angle, 1),
            "tilt_alert": tilt_alert,
            "anomalies_detected": anomalies,
            "recommendations": recommendations,
        }
