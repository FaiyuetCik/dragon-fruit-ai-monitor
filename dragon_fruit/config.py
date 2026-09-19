"""集中配置 — 模型路径、类别名、标签、阈值"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class MonitoringConfig:
    """火龙果监控系统全局配置"""

    # --- 路径 ---
    weights: Path = ROOT / "runs" / "train" / "exp4" / "weights" / "best.pt"
    data_yaml: Path = ROOT / "yolo_dataset" / "K.yaml"
    pest_weights: Optional[Path] = None
    output_dir: Path = ROOT / "runs" / "dragon_fruit"

    # --- 设备 ---
    device: str = ""

    # --- 成熟度检测 ---
    conf_thres: float = 0.25
    iou_thres: float = 0.45
    imgsz: tuple = (640, 640)

    # --- 类别映射 ---
    maturity_labels: dict = field(default_factory=lambda: {
        "shenghlg": {"en": "Unripe", "maturity": "unripe"},
        "huolongguo": {"en": "Ripe", "maturity": "ripe"},
    })

    # --- 病虫害类别 ---
    pest_disease_labels: dict = field(default_factory=lambda: {
        0: {"en": "Healthy"},
        1: {"en": "Aphids"},
        2: {"en": "Anthracnose"},
    })

    # --- 预处理 ---
    enable_clahe: bool = True
    enable_denoise: bool = True
    enable_brightness_contrast: bool = True
    target_size: tuple = (640, 640)

    # --- 生长异常阈值 ---
    greenness_threshold: float = 0.30
    yellowness_threshold: float = 0.15
    tilt_threshold: float = 15.0

    # --- 模块开关 ---
    enable_pest: bool = True
    enable_growth: bool = True
    enable_preprocess: bool = True

    # --- 日志 ---
    log_dir: Path = ROOT / "runs" / "dragon_fruit" / "logs"
