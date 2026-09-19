"""成熟度检测器 — 封装 YOLOv5 推理"""

from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
import torch

from models.common import DetectMultiBackend
from utils.general import non_max_suppression, scale_boxes
from utils.torch_utils import select_device

from dragon_fruit.config import MonitoringConfig
from dragon_fruit.detection.result_formatter import format_detections


class MaturityDetector:
    """火龙果成熟度检测器，封装 YOLOv5 目标检测模型。"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.device = select_device(config.device)
        self.model = DetectMultiBackend(
            str(config.weights), device=self.device, data=str(config.data_yaml), fp16=False
        )
        self.stride = self.model.stride
        self.names = self.model.names
        self.imgsz = config.imgsz
        self.model.warmup(imgsz=(1, 3, *self.imgsz))

    @torch.no_grad()
    def detect(self, preprocessed: torch.Tensor) -> List[dict]:
        """对预处理后的 tensor 运行推理。
        Args:
            preprocessed: 预处理后的 tensor (1, 3, H, W), float32, 0.0-1.0
        Returns:
            结构化检测结果列表
        """
        im = preprocessed.to(self.device)
        im = im.float()
        pred = self.model(im)
        pred = non_max_suppression(
            pred, self.config.conf_thres, self.config.iou_thres
        )
        det = pred[0]
        if det is None or len(det) == 0:
            return []

        det[:, :4] = scale_boxes(
            im.shape[2:], det[:, :4], self.original_shape
        ).round()
        self._last_det = det
        return format_detections(det, self.names, self.config)

    def annotate(self, image: np.ndarray, results: List[dict]) -> np.ndarray:
        """在图像上绘制带英文标签的边界框（使用 PIL 渲染）。
        Args:
            image: 原始 BGR 图像 (H, W, 3)
            results: detect() 返回的结果列表
        Returns:
            标注后的 BGR 图像
        """
        from dragon_fruit.pipeline.draw_utils import put_chinese_text_with_bg
        im = image.copy()
        for r in results:
            x1, y1, x2, y2 = map(int, r["bbox"])
            color = (0, 255, 0) if r.get("maturity") == "ripe" else (0, 165, 255)
            label = f"{r['label_en']} {r['confidence']:.2f}"
            cv2.rectangle(im, (x1, y1), (x2, y2), color, 2)
            put_chinese_text_with_bg(im, label, (x1, y1 - 24), font_size=16,
                                     text_color=(255, 255, 255), bg_color=(0, 0, 0, 140))
        return im

    def detect_on_image(self, image: np.ndarray, preprocessed: torch.Tensor) -> tuple:
        """对单张图像运行检测并返回结果和标注图。
        Args:
            image: 原始 BGR 图像 (H, W, 3)
            preprocessed: 预处理后的 tensor (1, 3, H, W)
        Returns:
            (results, annotated_image) 元组
        """
        self.original_shape = image.shape
        results = self.detect(preprocessed)
        annotated = self.annotate(image, results)
        return results, annotated
