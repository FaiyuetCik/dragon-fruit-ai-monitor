"""顶层调度器 — 编排全部检测模块"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import cv2

from dragon_fruit.config import MonitoringConfig
from dragon_fruit.preprocessing.pipeline import PreprocessingPipeline
from dragon_fruit.detection.maturity import MaturityDetector
from dragon_fruit.classification.pest_disease import PestDiseaseClassifier
from dragon_fruit.growth.anomaly import GrowthAnomalyDetector
from dragon_fruit.pipeline.alert import AlertEngine, Alert, LogWriter
from dragon_fruit.pipeline.report import (
    generate_summary_text,
    save_annotated_image,
    generate_json_report,
)


@dataclass
class MonitoringResult:
    image_path: str
    timestamp: str
    maturity_detections: List[dict] = field(default_factory=list)
    pest_disease_results: List[dict] = field(default_factory=list)
    growth_anomalies: dict = field(default_factory=dict)
    alerts: List[Alert] = field(default_factory=list)
    annotated_image_path: Optional[str] = None
    summary: str = ""


class DragonFruitMonitor:
    """火龙果 AI 监控系统顶层调度器。"""

    def __init__(self, config: MonitoringConfig = None):
        self.config = config or MonitoringConfig()
        self.preprocessor = PreprocessingPipeline(self.config) if self.config.enable_preprocess else None
        self.maturity_detector = MaturityDetector(self.config)
        self.pest_classifier = PestDiseaseClassifier(self.config) if self.config.enable_pest else None
        self.anomaly_detector = GrowthAnomalyDetector(self.config) if self.config.enable_growth else None
        self.alert_engine = AlertEngine()
        self.log_writer = LogWriter(self.config.log_dir)

    def process_image(self, image_path) -> MonitoringResult:
        """处理单张图像，返回完整监控结果。"""
        image_path = str(image_path)
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"无法读取图像: {image_path}")

        result = MonitoringResult(
            image_path=image_path,
            timestamp=datetime.now().isoformat(),
        )

        # 预处理
        if self.preprocessor:
            tensor = self.preprocessor(img)
        else:
            from dragon_fruit.preprocessing.transforms import resize_letterbox, to_tensor
            im = resize_letterbox(img, self.config.target_size)
            tensor = to_tensor(im)

        # 成熟度检测
        self.maturity_detector.original_shape = img.shape
        result.maturity_detections = self.maturity_detector.detect(tensor)

        # 病虫害分类
        if self.pest_classifier and self.config.enable_pest:
            if result.maturity_detections:
                result.pest_disease_results = [
                    cr[0] if cr else {"label_en": "Not detected", "confidence": 0.0}
                    for cr in self.pest_classifier.classify_crops(img, result.maturity_detections)
                ]
            else:
                # 无检测框时对整图分类
                result.pest_disease_results = self.pest_classifier.classify(img)

        # 生长异常
        if self.anomaly_detector and self.config.enable_growth:
            result.growth_anomalies = self.anomaly_detector.analyze(img)

        # 预警评估
        result.alerts = self.alert_engine.evaluate(result)

        # 日志记录
        self.log_writer.write_csv(result.alerts, image_path)

        # 摘要
        result.summary = generate_summary_text(result)

        return result

    def process_and_save(self, image_path, output_dir: Path = None) -> MonitoringResult:
        """处理图像并保存结果。
        Args:
            image_path: 输入图像路径
            output_dir: 输出目录，默认使用配置中的 output_dir
        Returns:
            MonitoringResult（含标注图路径）
        """
        output_dir = Path(output_dir or self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        img = cv2.imread(str(image_path))
        result = self.process_image(image_path)

        # 保存标注图像
        stem = Path(image_path).stem
        anno_path = output_dir / f"{stem}_annotated.jpg"
        save_annotated_image(img, result, anno_path)
        result.annotated_image_path = str(anno_path)

        # 保存 JSON 日志
        json_path = output_dir / f"{stem}_result.json"
        self.log_writer.write_json_log(result, json_path)

        return result

    def process_directory(self, dir_path, output_dir: Path = None) -> List[MonitoringResult]:
        """批量处理目录中所有图像。"""
        dir_path = Path(dir_path)
        output_dir = Path(output_dir or self.config.output_dir)
        image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}

        images = sorted([f for f in dir_path.iterdir()
                        if f.suffix.lower() in image_exts])
        results = []
        for i, img_path in enumerate(images):
            try:
                result = self.process_and_save(img_path, output_dir)
                results.append(result)
                print(f"[{i+1}/{len(images)}] {result.summary}")
            except Exception as e:
                print(f"[{i+1}/{len(images)}] 错误: {img_path.name} - {e}")

        # 批量 JSON 报告
        report_path = output_dir / "batch_report.json"
        generate_json_report(results, report_path)
        print(f"\n批量报告已保存: {report_path}")
        print(f"预警日志: {self.config.log_dir}")

        return results
