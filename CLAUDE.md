# Dragon Fruit AI Vision Monitoring System

## Overview

AI-powered dragon fruit orchard monitoring system built on YOLOv5 + OpenCV. Features: fruit maturity detection, pest/disease identification (aphids/anthracnose), growth anomaly detection (yellowing/tilting/low greenery). Supports CLI batch mode and Gradio web interface (with public share links).

## Environment

- Isolated Python 3.12.7: `.venv\Scripts\python.exe`
- Use `start_monitor.cmd` (local Web UI at http://127.0.0.1:7860) or pass CLI arguments to it.
- PyTorch 2.6.0+cpu / torchvision 0.21.0+cpu; no CUDA required.
- NumPy 1.26.4, pandas 2.2.3, OpenCV 4.11.0.86, Gradio 4.44.1, Ultralytics 8.3.40.
- The Anaconda base environment is NOT the project runtime (it has incompatible NumPy / pandas binaries).
- `requirements-monitor.txt`: direct version pins; `requirements-monitor.lock.txt`: full tested dependency lock.
- `ENVIRONMENT.md`: launch, rebuild and verification instructions.
- `verify_monitor_environment.py`: real batch inference + local Gradio API and download verification.
- Launch/verification scripts isolate Ultralytics settings under `.venv/runtime/ultralytics`.
- Commands below using `python` assume the project `.venv` is activated.
- Node.js is only used for Word report generation.

## Project Structure

```
<project-root>\
  # === Original YOLOv5 files (DO NOT MODIFY) ===
  detect.py              # Defaults to exp4/best.pt + K.yaml
  train.py               # Training script
  classify/train.py      # Classification training (for pest/disease)
  models/common.py        # DetectMultiBackend etc.
  utils/augmentations.py  # letterbox(), ToTensor, hist_equalize()
  utils/dataloaders.py    # LoadStreams, LoadImages
  utils/general.py        # NMS, scale_boxes, cv2
  export.py               # Model export (TFLite/ONNX/TorchScript)

  # === Custom dataset ===
  yolo_dataset/
    K.yaml                # 2 classes: shenghlg (unripe), huolongguo (ripe)
    images/               # train 54 / val 9 / test 7
    labels/               # YOLO format annotations

  # === Training artifacts ===
  runs/train/exp4/        # Best model: mAP@0.5=0.995
  runs/train/exp8/        # Latest (worse than exp4)
  runs/detect/            # Detection results

  # === New code (this project) ===
  dragon_fruit_monitor.py  # Entry point
  dragon_fruit/            # Core package (zero-intrusion on YOLOv5)
    __init__.py             # Path init + torch.load compat fix (PyTorch 2.6+)
    config.py               # MonitoringConfig dataclass
    cli.py                  # CLI (argparse)

    preprocessing/          # Image preprocessing pipeline
      pipeline.py           #   PreprocessingPipeline orchestrator
      enhancers.py          #   CLAHE, brightness/contrast
      denoisers.py          #   Gaussian/NLM denoising
      transforms.py         #   letterbox + tensor conversion

    detection/              # Maturity detection
      maturity.py           #   MaturityDetector (wraps DetectMultiBackend)
      result_formatter.py   #   Raw predictions → structured output

    classification/         # Pest/disease classification
      pest_disease.py       #   PestDiseaseClassifier (graceful degradation)

    growth/                 # Growth anomaly detection (pure CV, no DL)
      anomaly.py            #   GrowthAnomalyDetector orchestrator
      color_analysis.py     #   HSV greenness index + yellowness ratio
      geometry.py           #   Canny + Hough tilt detection

    pipeline/               # Top-level orchestration
      orchestrator.py       #   DragonFruitMonitor
      report.py             #   JSON report + annotated image (PIL text)
      alert.py              #   AlertEngine (6 rules) + LogWriter (CSV/JSON)
      draw_utils.py         #   PIL-based text rendering (cv2.putText can't render non-ASCII)

    web/                    # Web interface
      app.py                #   Gradio UI with custom CSS (--serve to launch)
                            #   Public share link, HTML tables, download buttons
                            #   Styled: warm palette, white cards, high contrast

    data/                   # Data augmentation
      augmentation.py       #   Offline augmentation (flip/rotate/brightness/HSV)
      retrain.py            #   Re-training launcher
      train_pest.py         #   Pest classifier training launcher
      pest_dataset/         #   Pest dataset dir (3 classes: Healthy/Aphids/Anthracnose)
      README.md             #   Data collection guide

    generate_report.js      # Node.js script to generate Word report
    Dragon_Fruit_AI_Vision_Monitoring_System_Report.docx
```

## Key Design Decisions

1. **Zero intrusion**: dragon_fruit/ never modifies YOLOv5 files — only imports and reuses
2. **Class-based**: Each module is a class with constructor-injected config; easy to test and swap
3. **Centralized config**: MonitoringConfig dataclass manages all paths, thresholds, toggles
4. **MonitoringResult contract**: Well-defined JSON-serializable output across all modules
5. **Pure CV for growth anomalies**: No training data or GPU needed — works immediately
6. **Graceful degradation**: Pest classifier skips silently when model not trained
7. **PIL text rendering**: All labels use PIL/Pillow. cv2.putText() does NOT support non-ASCII characters (renders as `????`)

## Usage

```bash
cd <project-root>

# Analyze single image (auto timestamp subdirectory)
python dragon_fruit_monitor.py --source yolo_dataset/images/test/1.png

# Batch process a directory
python dragon_fruit_monitor.py --source yolo_dataset/images/test/ --output results/

# Custom model / thresholds
python dragon_fruit_monitor.py --source img.jpg --weights runs/train/exp8/weights/best.pt --conf-thres 0.5

# Disable modules
python dragon_fruit_monitor.py --source img.jpg --no-pest --no-growth --no-preprocess

# Launch Gradio web UI (public share link)
python dragon_fruit_monitor.py --serve --port 7860
# --no-share for local-only; public link valid 1 week via *.gradio.live
# frpc required: C:\Users\<user>\.cache\huggingface\gradio\frpc\frpc_windows_amd64_v0.3
```

## Output Files

Each analysis generates under `runs/dragon_fruit/{timestamp}/` (auto timestamp when `--output` not specified):
- `{name}_annotated.jpg` — Annotated image (bounding boxes + anomaly info + alerts)
- `{name}_result.json` — Full JSON result per image
- `batch_report.json` — Batch summary (directory mode only)
- `logs/alerts_YYYY-MM-DD.csv` — Date-archived alert log

Web mode results save to `runs/dragon_fruit/web/`.

## Technical Details

### torch.load Compatibility Fix
PyTorch 2.6+ defaults `weights_only=True`, breaking YOLOv5 model loading.
Fix: `dragon_fruit/__init__.py` monkey-patches `torch.load` to add `weights_only=False`.

### NumPy Version
Must use `numpy<2` (currently 1.26.4). NumPy 2.x crashes pandas/pyarrow.

### Maturity Model
- exp4/best.pt: mAP@0.5=0.995, Recall=1.0 (current default)
- exp8/best.pt: mAP@0.5=0.667 (inferior)
- All training based on yolov5s.pt pretrained weights

### Alert Rules
| Rule | Level | Trigger |
|------|-------|---------|
| anthracnose_detected | CRITICAL | Pest classifier reports Anthracnose |
| aphids_detected | WARNING | Pest classifier reports Aphids |
| no_ripe_fruit | INFO | No ripe fruit detected |
| leaf_yellowing | WARNING | Yellowness ratio > 15% |
| plant_tilting | WARNING | Tilt angle > 15 deg |
| low_greenness | WARNING | Greenness index < 30% |

### Growth Anomaly Thresholds (adjustable in config.py)
- Greenness threshold: 0.30 (warn below)
- Yellowness threshold: 0.15 (warn above)
- Tilt threshold: 15.0 deg (warn above)

### Gradio NO_PROXY Fix
Gradio startup fails with 502 if proxy is configured. Fix in `web/app.py`: sets `NO_PROXY=localhost,127.0.0.1` before launch.

### Gradio Public Share Link (frpc)
Public links require frpc binary. If blocked by firewall, download manually:
1. Download `https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_windows_amd64.exe`
2. Rename to `frpc_windows_amd64_v0.3`
3. Place in `C:\Users\<user>\.cache\huggingface\gradio\frpc\`

### Web UI Design
Custom CSS (no Gradio theme dependency). White cards, warm amber accents, high-contrast text. HTML tables with badges replace raw markdown. Accordion labels white on dark bg. Download buttons for JSON + annotated JPG. JS injection for shadow DOM filename text color fix.

## Future Work

1. Real-time camera capture (YOLOv5's LoadStreams already supports this — needs hardware)
2. Edge deployment (export.py → TFLite/ONNX)
3. Pest dataset collection + training (directory structure ready, run train_pest.py)
4. Data augmentation expansion (run augmentation.py → retrain.py)
5. More pest/disease categories