"""重训练脚本 — 使用增强后的数据集重新训练成熟度检测模型

用法:
    python dragon_fruit/data/retrain.py --epochs 100 --batch 16 --img 640
"""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="重训练 YOLOv5 成熟度检测模型")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--img", type=int, default=640)
    parser.add_argument("--weights", type=str, default="yolov5s.pt")
    parser.add_argument("--name", type=str, default="exp_augmented")
    args = parser.parse_args()

    # 检查增强数据是否存在，否则使用原始数据
    aug_images = ROOT / "yolo_dataset" / "images" / "train_augmented"
    data_yaml = ROOT / "yolo_dataset" / "K.yaml"

    if aug_images.exists() and any(aug_images.iterdir()):
        print(f"使用增强数据集: {aug_images}")
        # 创建合并数据集 YAML
        import yaml
        with open(data_yaml, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        cfg["train"] = str(aug_images)
        merged_yaml = ROOT / "yolo_dataset" / "K_augmented.yaml"
        with open(merged_yaml, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, allow_unicode=True)
        data_arg = str(merged_yaml)
    else:
        print("增强数据集不存在，使用原始数据")
        data_arg = str(data_yaml)

    cmd = [
        sys.executable, str(ROOT / "train.py"),
        "--data", data_arg,
        "--weights", args.weights,
        "--epochs", str(args.epochs),
        "--batch-size", str(args.batch),
        "--img", str(args.img),
        "--project", str(ROOT / "runs" / "train"),
        "--name", args.name,
    ]
    print(f"执行训练: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    main()
