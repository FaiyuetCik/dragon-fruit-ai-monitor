"""预警与日志系统"""

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List


class AlertLevel(Enum):
    INFO = "INFO"          # 正常
    WARNING = "WARNING"    # 注意
    CRITICAL = "CRITICAL"  # 严重


@dataclass
class Alert:
    level: AlertLevel
    rule_name: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AlertRule:
    name: str
    level: AlertLevel
    description: str
    evaluate: callable  # (MonitoringResult) -> Optional[str]  返回消息或 None


class AlertEngine:
    """预警规则引擎。评估 MonitoringResult 并生成预警列表。"""

    def __init__(self):
        self.rules: List[AlertRule] = []
        self._register_default_rules()

    def _register_default_rules(self):
        self.rules = [
            AlertRule("anthracnose_detected", AlertLevel.CRITICAL,
                      "Anthracnose detected",
                      lambda r: "Anthracnose detected! Immediate treatment required."
                      if any(p.get("label_en") == "Anthracnose"
                             for p in r.pest_disease_results) else None),
            AlertRule("aphids_detected", AlertLevel.WARNING,
                      "Aphids detected",
                      lambda r: "Aphid infestation detected. Recommend spraying."
                      if any(p.get("label_en") == "Aphids"
                             for p in r.pest_disease_results) else None),
            AlertRule("no_ripe_fruit", AlertLevel.INFO,
                      "No ripe fruit",
                      lambda r: "No ripe dragon fruit detected. Continue monitoring."
                      if len(r.maturity_detections) == 0 else None),
            AlertRule("leaf_yellowing", AlertLevel.WARNING,
                      "Leaf yellowing",
                      lambda r: "Leaf yellowing detected. Check for nutrient deficiency or disease."
                      if r.growth_anomalies.get("yellowness_alert") else None),
            AlertRule("plant_tilting", AlertLevel.WARNING,
                      "Plant tilting",
                      lambda r: f"Plant tilted {r.growth_anomalies.get('tilt_angle_degrees', 0)} deg. Check support structure."
                      if r.growth_anomalies.get("tilt_alert") else None),
            AlertRule("low_greenness", AlertLevel.WARNING,
                      "Low greenery",
                      lambda r: "Low greenery index. Check soil nutrients and irrigation."
                      if r.growth_anomalies.get("greenness_status") == "low" else None),
        ]

    def evaluate(self, result) -> List[Alert]:
        """评估监控结果，返回触发的预警列表。"""
        alerts = []
        for rule in self.rules:
            try:
                msg = rule.evaluate(result)
                if msg:
                    alerts.append(Alert(level=rule.level, rule_name=rule.name, message=msg))
            except Exception:
                pass
        return alerts


class LogWriter:
    """日志写入器 — CSV + JSON 双格式。"""

    def __init__(self, log_dir: Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def write_csv(self, alerts: List[Alert], image_path: str):
        date_str = datetime.now().strftime("%Y-%m-%d")
        csv_path = self.log_dir / f"alerts_{date_str}.csv"
        file_exists = csv_path.exists()
        with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "image_path", "level", "rule", "message"])
            if not file_exists:
                writer.writeheader()
            for a in alerts:
                writer.writerow({
                    "timestamp": a.timestamp,
                    "image_path": image_path,
                    "level": a.level.value,
                    "rule": a.rule_name,
                    "message": a.message,
                })

    def write_json_log(self, result, output_path: Path):
        """将完整 MonitoringResult 写入 JSON 日志。"""
        import dataclasses
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "image_path": result.image_path,
            "timestamp": result.timestamp,
            "maturity_detections": result.maturity_detections,
            "pest_disease_results": result.pest_disease_results,
            "growth_anomalies": result.growth_anomalies,
            "alerts": [{"level": a.level.value, "rule": a.rule_name, "message": a.message}
                       for a in result.alerts],
            "summary": result.summary,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
