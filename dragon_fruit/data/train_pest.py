"""病虫害分类模型训练脚本 — 复用 YOLOv5 classify 模块"""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATASET = Path(__file__).resolve().parent / "pest_dataset"


def main():
    if not (DATASET / "train").exists():
        print(f"错误：数据集目录不存在: {DATASET / 'train'}")
        print("请先按 README.md 说明收集数据，放入对应类别文件夹。")
        sys.exit(1)

    # 统计各类别样本数
    for split in ["train", "val"]:
        split_dir = DATASET / split
        if not split_dir.exists():
            continue
        print(f"[{split}]")
        for cls_dir in sorted(split_dir.iterdir()):
            if cls_dir.is_dir():
                count = len(list(cls_dir.glob("*")))
                print(f"  {cls_dir.name}: {count} 张")

    # 调用 YOLOv5 classify/train.py
    cmd = [
        sys.executable, str(ROOT / "classify" / "train.py"),
        "--model", "yolov5s-cls.pt",
        "--data", str(DATASET),
        "--epochs", "50",
        "--img", "224",
        "--batch", "32",
        "--project", str(ROOT / "runs" / "train-pest"),
    ]
    print(f"\n执行训练: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    main()
