"""原始预测结果 → 结构化输出"""

from typing import List, Optional

from dragon_fruit.config import MonitoringConfig


def format_detections(
    detections,              # NMS 输出 tensor (n, 6): [x1, y1, x2, y2, conf, cls]
    names: dict,             # 类别索引 → 英文名
    config: MonitoringConfig,
) -> List[dict]:
    """将原始检测结果格式化为结构化字典列表。
    Args:
        detections: YOLOv5 NMS 输出的 tensor
        names: 类别索引到名称的映射
        config: 全局配置
    Returns:
        检测结果列表
    """
    results = []
    if detections is None or len(detections) == 0:
        return results

    for *xyxy, conf, cls in detections:
        class_idx = int(cls)
        class_name = names.get(class_idx, str(class_idx))
        label_info = config.maturity_labels.get(class_name, {})
        results.append({
            "class_name": class_name,
            "label_en": label_info.get("en", class_name),
            "maturity": label_info.get("maturity", "unknown"),
            "confidence": round(float(conf), 4),
            "bbox": [round(float(x), 1) for x in xyxy],
        })
    return results
