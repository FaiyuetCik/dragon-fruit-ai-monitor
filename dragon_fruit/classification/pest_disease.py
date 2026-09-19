"""病虫害分类器 — CNN 图像分类，检测蚜虫、炭疽病等"""

import logging
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
import torch

from dragon_fruit.config import MonitoringConfig

logger = logging.getLogger(__name__)


class PestDiseaseClassifier:
    """病虫害 CNN 分类器。
    若模型权重未提供，自动降级跳过。
    """

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.model = None
        self.names = {}
        self._loaded = False

        if config.pest_weights and Path(config.pest_weights).exists():
            self._load_model()
        else:
            logger.info("Pest model not configured. Pest detection will be skipped.")

    def _load_model(self):
        """加载分类模型。"""
        try:
            from models.common import DetectMultiBackend
            from utils.torch_utils import select_device

            device = select_device(self.config.device)
            self.model = DetectMultiBackend(
                str(self.config.pest_weights), device=device, dnn=False, data=None, fp16=False
            )
            for k, v in self.config.pest_disease_labels.items():
                self.names[int(k)] = v
            self._loaded = True
            logger.info(f"病虫害模型已加载: {self.config.pest_weights}")
        except Exception as e:
            logger.warning(f"病虫害模型加载失败: {e}，将跳过病虫害检测。")

    @property
    def available(self) -> bool:
        return self._loaded and self.model is not None

    def classify(self, image: np.ndarray, top_k: int = 3) -> List[dict]:
        """对单张图像进行分类。
        Args:
            image: BGR 图像 (H, W, 3), uint8
            top_k: 返回前 k 个预测
        Returns:
            [{"label_en": "Healthy", "confidence": 0.95, ...}, ...]
        """
        if not self.available:
            return [{"label_en": "Not detected", "confidence": 0.0,
                     "note": "Pest model not loaded"}]

        from utils.augmentations import classify_transforms

        im = classify_transforms((224, 224))(image)
        im = im.unsqueeze(0).to(self.model.device)

        with torch.no_grad():
            pred = self.model(im)
            if isinstance(pred, (list, tuple)):
                pred = pred[0]
            probs = torch.softmax(pred, dim=1)[0]

        top_indices = probs.argsort(descending=True)[:top_k]
        results = []
        for idx in top_indices:
            idx_int = int(idx)
            info = self.names.get(idx_int, {"en": f"class_{idx_int}"})
            results.append({
                "class_id": idx_int,
                "label_en": info.get("en", info.get("cn", f"class_{idx_int}")),
                "confidence": round(float(probs[idx]), 4),
            })
        return results

    def classify_crops(self, image: np.ndarray,
                       detection_boxes: List[dict]) -> List[List[dict]]:
        """对检测到的果实区域逐一分类。
        Args:
            image: 完整 BGR 图像
            detection_boxes: 成熟度检测的边界框列表
        Returns:
            每个果实的分类结果列表
        """
        results = []
        for det in detection_boxes:
            x1, y1, x2, y2 = map(int, det["bbox"])
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
            crop = image[y1:y2, x1:x2]
            if crop.size > 0:
                results.append(self.classify(crop))
            else:
                results.append([])
        return results
