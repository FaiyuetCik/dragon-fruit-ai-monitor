"""预处理流水线编排器"""

import numpy as np
import torch

from dragon_fruit.config import MonitoringConfig
from dragon_fruit.preprocessing.enhancers import apply_clahe, adjust_brightness_contrast
from dragon_fruit.preprocessing.denoisers import denoise_fast
from dragon_fruit.preprocessing.transforms import resize_letterbox, to_tensor


class PreprocessingPipeline:
    """图像预处理流水线：增强 → 降噪 → 尺寸调整 → 归一化"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.target_size = config.target_size

    def __call__(self, image: np.ndarray) -> torch.Tensor:
        """运行完整预处理流水线。
        Args:
            image: BGR uint8 图像 (H, W, 3)
        Returns:
            RGB float32 tensor (1, 3, target_h, target_w), 0.0-1.0
        """
        im = image.copy()

        if self.config.enable_brightness_contrast:
            im = adjust_brightness_contrast(im)

        if self.config.enable_clahe:
            im = apply_clahe(im)

        if self.config.enable_denoise:
            im = denoise_fast(im)

        im = resize_letterbox(im, self.target_size)
        im = to_tensor(im)
        return im
