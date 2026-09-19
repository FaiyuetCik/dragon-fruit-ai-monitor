# Dragon Fruit AI Vision Monitor

A dragon fruit image-analysis project built on YOLOv5, OpenCV and Gradio. It detects ripe and unripe fruit, reports bounding boxes and confidence scores, and exports annotated images, JSON reports and alert logs.

[中文说明](README.md) · [Environment guide (Chinese)](ENVIRONMENT.md)

> This repository is the source code and demonstration framework for a local dragon fruit maturity image-analysis system. It supports still-image detection, batch processing, result reports and basic anomaly indicators. The code path is runnable locally, but trained weights and training data are intentionally kept out of the repository; users must provide a compatible `best.pt` and their own images.

## Current capabilities

- **Maturity detection:** two classes, `shenghlg` (unripe) and `huolongguo` (ripe), using a separately trained YOLOv5 checkpoint.
- **Image preprocessing:** brightness/contrast adjustment, CLAHE, denoising and resizing.
- **Growth analysis:** HSV greenness/yellowness and line-based tilt estimates. These are heuristic indicators awaiting field validation.
- **Web interface:** single-image upload, result tables, alerts and JSON/annotated-image downloads.
- **Batch processing:** process a directory through the CLI and save individual and combined reports.
- **Pest/disease interface:** classifier integration exists for Healthy, Aphids and Anthracnose, but no trained classifier is supplied. A skipped classifier does not establish that an image is disease-free.

The custom application currently processes still images. Continuous camera monitoring, historical dashboards and external alert delivery are not implemented.

## Required local assets

**This repository contains source code, configuration and dependency lists. Training images and labels are private and are not included. It does not include trained checkpoints, original images, generated results or a virtual environment. Cloning alone is not enough to run detection.**

Provide a compatible YOLOv5 checkpoint trained on the two dragon fruit classes above, in that order. The web application loads `runs/train/exp4/weights/best.pt` by default; create that directory and place the checkpoint there, or change `MonitoringConfig.weights` in [config.py](dragon_fruit/config.py). The CLI also accepts `--weights`.

A generic `yolov5s.pt` is not a replacement for the dragon fruit maturity checkpoint. No public download for the custom weights is currently provided.

For training, supply your own images and labels under your local dataset directories. Training data is not included in this repository.

## Setup: Windows, Python 3.12, CPU

With Python 3.12 and Git installed, run in PowerShell:

```powershell
git clone https://github.com/FaiyuetCik/dragon-fruit-ai-monitor.git
cd dragon-fruit-ai-monitor
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install "torch==2.6.0+cpu" "torchvision==0.21.0+cpu" --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements-monitor.lock.txt
.\.venv\Scripts\python.exe -m pip check
```

If the `py` launcher is unavailable, use your Python 3.12 executable instead. The lock file includes the locally verified NumPy 1.26.4 and Gradio 4.44.1 versions.

## Run

After installing dependencies and placing the checkpoint at its default location, double-click `start_monitor.cmd` or run:

```powershell
.\start_monitor.cmd
```

Open http://127.0.0.1:7860, upload an image and click **Analyze**. The launcher uses local-only mode. Press Ctrl+C to stop.

The current `--serve` branch does not apply CLI analysis options such as `--weights` or `--pest-weights`. Configure web models through their default locations or [config.py](dragon_fruit/config.py).

For CLI use, place your own images in `input/`; filenames below are examples:

```powershell
.\start_monitor.cmd --source input/fruit.jpg --output runs/example
.\start_monitor.cmd --source input --output runs/batch
.\start_monitor.cmd --source input/fruit.jpg --weights models/local-best.pt --conf-thres 0.5
.\start_monitor.cmd --source input/fruit.jpg --no-pest --no-growth
```

## Outputs and layout

Each image produces `<name>_annotated.jpg` and `<name>_result.json`. Directory processing also creates `batch_report.json`; alert logs are stored in `logs/alerts_<date>.csv`.

CLI outputs default to `runs/dragon_fruit/<timestamp>/`; web outputs go to `runs/dragon_fruit/web/`.

The application code is in [dragon_fruit/](dragon_fruit/), with modules for preprocessing, detection, classification, growth analysis, pipeline orchestration and the web interface. The CLI entry point is `dragon_fruit_monitor.py`. The root scripts and `models/`, `utils/` directories retain the YOLOv5 foundation.

## Verification and limitations

Local verification on 2026-09-19 passed batch processing of 7 images and web upload, inference and file downloads. This verifies execution, not field accuracy.

`verify_monitor_environment.py` requires the local checkpoint and the original seven test images under `yolo_dataset/images/test/`, including `1.png`. These assets are not published, so this check cannot run on a fresh clone without them:

```powershell
.\.venv\Scripts\python.exe verify_monitor_environment.py
```

A successful check saves `runs/environment-check/<timestamp>/verification.json`.

The dataset is small and needs independent evaluation under varied lighting, backgrounds and occlusion. Growth indicators can be affected by the background. The current “no ripe fruit” rule only fires when there are no fruit detections at all; it still needs to handle images containing only unripe fruit.

## Attribution and license

Built on [Ultralytics YOLOv5](https://github.com/ultralytics/yolov5), retaining upstream code and its license. The dragon fruit application is in `dragon_fruit/`. See [LICENSE](LICENSE) for GNU AGPL v3 and [CITATION.cff](CITATION.cff) for the upstream YOLOv5 citation.
