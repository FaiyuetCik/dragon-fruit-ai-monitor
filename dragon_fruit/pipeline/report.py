"""报告生成 — JSON 报告、注释图像、中文摘要"""

import json
from pathlib import Path
from typing import List

import cv2
import numpy as np

from dragon_fruit.pipeline.draw_utils import put_chinese_text, put_chinese_text_with_bg


def generate_summary_text(result) -> str:
    """Generate a one-line English summary from MonitoringResult."""
    parts = []

    # Maturity
    n = len(result.maturity_detections)
    if n == 0:
        parts.append("No dragon fruit detected")
    else:
        ripe = sum(1 for d in result.maturity_detections if d.get("maturity") == "ripe")
        unripe = n - ripe
        parts.append(f"Detected {n} fruit (ripe {ripe}, unripe {unripe})")

    # Pest & Disease
    if result.pest_disease_results:
        pests = [r for r in result.pest_disease_results
                 if r and r.get("label_en") not in ("Healthy", "Not detected")]
        if pests:
            parts.append(f"Pest: {', '.join(p['label_en'] for p in pests)}")
        else:
            parts.append("Pest: none detected")

    # Growth anomalies
    anomalies = result.growth_anomalies.get("anomalies_detected", [])
    if anomalies:
        parts.append(f"Growth anomalies: {len(anomalies)}")
    else:
        parts.append("Growth: normal")

    # Alerts
    if result.alerts:
        crit = [a for a in result.alerts if a.level.value == "CRITICAL"]
        warn = [a for a in result.alerts if a.level.value == "WARNING"]
        if crit:
            parts.append(f"CRITICAL: {len(crit)}")
        if warn:
            parts.append(f"WARNING: {len(warn)}")

    return "; ".join(parts)


def save_annotated_image(image: np.ndarray, result, output_path: Path) -> Path:
    """保存综合标注图像（成熟度框 + 中文标注 + 生长异常信息）。
    使用 PIL 渲染中文文本（OpenCV putText 不支持中文）。
    """
    im = image.copy()

    # --- 成熟度边界框 + 中文标签 ---
    for d in result.maturity_detections:
        x1, y1, x2, y2 = map(int, d["bbox"])
        box_color = (0, 255, 0) if d.get("maturity") == "ripe" else (0, 165, 255)
        cv2.rectangle(im, (x1, y1), (x2, y2), box_color, 2)
        label = f'{d["label_en"]} {d["confidence"]:.2f}'
        put_chinese_text_with_bg(im, label, (x1, y1 - 24), font_size=16,
                                 text_color=(255, 255, 255), bg_color=(0, 0, 0, 210))

    # --- 左上角信息面板 ---
    y_offset = 10
    line_height = 22
    ga = result.growth_anomalies
    info_lines = [
        f"greenness: {ga.get('greenness_index', 0):.2f}  "
        f"yellowness: {ga.get('yellowness_ratio', 0):.2f}  "
        f"tilt: {ga.get('tilt_angle_degrees', 0):.1f} deg",
    ]
    anomalies = ga.get("anomalies_detected", [])
    if anomalies:
        info_lines.append(f"anomalies: {', '.join(anomalies)}")
    else:
        info_lines.append("anomalies: none")

    for line in info_lines:
        put_chinese_text_with_bg(im, line, (10, y_offset), font_size=14,
                                 text_color=(255, 255, 255), bg_color=(0, 0, 0, 210))
        y_offset += line_height

    # --- 预警信息 ---
    for alert in result.alerts:
        if alert.level.value == "CRITICAL":
            bg = (50, 0, 0, 230)
        elif alert.level.value == "WARNING":
            bg = (50, 30, 0, 230)
        else:
            bg = (0, 40, 0, 230)

        msg = f"[{alert.level.value}] {alert.message}"
        put_chinese_text_with_bg(im, msg, (10, y_offset), font_size=14,
                                 text_color=(255, 255, 255), bg_color=bg)
        y_offset += line_height

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), im)
    return output_path


def generate_json_report(results: List, output_path: Path) -> Path:
    """生成批量处理结果的 JSON 报告。"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = []
    for r in results:
        data.append({
            "image_path": r.image_path,
            "timestamp": r.timestamp,
            "maturity_detections": r.maturity_detections,
            "pest_disease_results": r.pest_disease_results,
            "growth_anomalies": r.growth_anomalies,
            "alerts": [{"level": a.level.value, "rule": a.rule_name, "message": a.message}
                       for a in r.alerts],
            "summary": r.summary,
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return output_path
