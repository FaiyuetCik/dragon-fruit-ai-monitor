"""离线数据增强 — 扩充训练集，提升模型泛化能力"""

import random
from pathlib import Path

import cv2
import numpy as np


def augment_image(image: np.ndarray) -> list:
    """对单张图像应用多种增强，返回增强后的图像列表。
    Args:
        image: BGR 图像 (H, W, 3), uint8
    Returns:
        增强图像列表（不含原图）
    """
    results = []

    # 1. 水平翻转
    results.append(cv2.flip(image, 1))

    # 2. 旋转 90°、180°、270°
    h, w = image.shape[:2]
    for angle in [90, 180, 270]:
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h))
        results.append(rotated)

    # 3. 亮度调整（暗化 + 亮化）
    for beta in [-30, 30]:
        adjusted = cv2.convertScaleAbs(image, alpha=1.0, beta=beta)
        results.append(adjusted)

    # 4. 对比度调整
    for alpha in [0.7, 1.3]:
        adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=0)
        results.append(adjusted)

    # 5. 高斯模糊
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    results.append(blurred)

    # 6. HSV 色调微调
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    for shift in [-10, 10]:
        hsv_shifted = hsv.copy()
        hsv_shifted[:, :, 0] = (hsv_shifted[:, :, 0] + shift) % 180
        results.append(cv2.cvtColor(hsv_shifted.astype(np.uint8), cv2.COLOR_HSV2BGR))

    return results


def expand_dataset(
    images_dir: Path,
    labels_dir: Path,
    output_images_dir: Path,
    output_labels_dir: Path,
    max_per_image: int = 10,
):
    """对标注数据集进行离线增强。
    Args:
        images_dir: 原始图像目录
        labels_dir: 原始标注目录（YOLO 格式 txt）
        output_images_dir: 输出图像目录
        output_labels_dir: 输出标注目录
        max_per_image: 每张原图最多生成的增强样本数
    """
    output_images_dir.mkdir(parents=True, exist_ok=True)
    output_labels_dir.mkdir(parents=True, exist_ok=True)

    image_files = sorted(images_dir.glob("*"))
    image_files = [f for f in image_files if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}]

    total = 0
    for img_path in image_files:
        stem = img_path.stem
        label_path = labels_dir / f"{stem}.txt"

        img = cv2.imread(str(img_path))
        if img is None:
            continue

        augmented = augment_image(img)
        random.shuffle(augmented)
        augmented = augmented[:max_per_image]

        for i, aug_img in enumerate(augmented):
            aug_stem = f"{stem}_aug{i}"
            cv2.imwrite(str(output_images_dir / f"{aug_stem}.jpg"), aug_img)

            # 复制原标注文件（边界框对空间变换增强不准确，但对颜色/亮度增强有效）
            if label_path.exists():
                import shutil
                shutil.copy(str(label_path), str(output_labels_dir / f"{aug_stem}.txt"))

            total += 1

    print(f"数据增强完成: 原始 {len(image_files)} 张 → 新增 {total} 张增强样本")
    return total


if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parents[2]
    images_dir = ROOT / "yolo_dataset" / "images" / "train"
    labels_dir = ROOT / "yolo_dataset" / "labels" / "train"
    out_images = ROOT / "yolo_dataset" / "images" / "train_augmented"
    out_labels = ROOT / "yolo_dataset" / "labels" / "train_augmented"

    expand_dataset(images_dir, labels_dir, out_images, out_labels)
