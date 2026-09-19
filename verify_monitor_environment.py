"""Verify the isolated runtime using real inference and a local Gradio API request."""
import os
os.environ["NO_PROXY"] = "localhost,127.0.0.1," + os.environ.get("NO_PROXY", "")
os.environ["no_proxy"] = os.environ["NO_PROXY"]
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["YOLOv5_AUTOINSTALL"] = "False"
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
os.environ["YOLO_CONFIG_DIR"] = str(ROOT / ".venv" / "runtime" / "ultralytics")
Path(os.environ["YOLO_CONFIG_DIR"]).mkdir(parents=True, exist_ok=True)
OUTPUT = ROOT / "runs" / "environment-check" / datetime.now().strftime("%Y%m%d-%H%M%S")
OUTPUT.mkdir(parents=True, exist_ok=True)
subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
subprocess.run([
    sys.executable, "dragon_fruit_monitor.py", "--source", "yolo_dataset/images/test",
    "--output", str(OUTPUT / "batch"),
], check=True)
reports = sorted((OUTPUT / "batch").glob("*_result.json"))
assert len(reports) == 7, f"Expected 7 image reports, got {len(reports)}"
count = 0
for path in reports:
    data = json.loads(path.read_text(encoding="utf-8"))
    count += len(data["maturity_detections"])
    image = path.with_name(path.name.replace("_result.json", "_annotated.jpg"))
    assert image.is_file() and image.stat().st_size > 0
assert count > 0, "No fruit detections across all 7 test images"

from dragon_fruit.config import MonitoringConfig
from dragon_fruit.pipeline.orchestrator import DragonFruitMonitor
from dragon_fruit.web import app
from gradio_client import Client, handle_file
config = MonitoringConfig(output_dir=OUTPUT / "web", log_dir=OUTPUT / "web" / "logs")
app._monitor = DragonFruitMonitor(config)
demo = app.build_interface()
try:
    _, url, _ = demo.launch(server_name="127.0.0.1", server_port=17860,
                          share=False, prevent_thread_lock=True, quiet=True)
    opener = build_opener(ProxyHandler({}))
    assert opener.open(url, timeout=20).status == 200
    client = Client(url, verbose=False)
    result = client.predict(handle_file(str(ROOT / "yolo_dataset/images/test/1.png")),
                            api_name="/analyze")
    assert len(result) == 9, f"Unexpected UI outputs: {len(result)}"
    assert result[0] and result[7] and result[8], "Missing UI image or download outputs"
    for index in (0, 7, 8):
        assert Path(result[index]).is_file(), f"Missing downloaded UI output {index}"
    summary = {"status": "PASS", "python": sys.executable, "batch_images": len(reports),
               "fruit_detections": count, "web_http": 200, "web_api": "PASS",
               "web_summary": result[1], "output_dir": str(OUTPUT)}
    (OUTPUT / "verification.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
finally:
    demo.close()