"""绘图工具 — 用 PIL 渲染中文文本（OpenCV putText 不支持中文）"""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# 查找系统中文字体
def _find_chinese_font() -> str:
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",       # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",     # 黑体
        "C:/Windows/Fonts/simsun.ttc",     # 宋体
        "C:/Windows/Fonts/simkai.ttf",     # 楷体
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    return "C:/Windows/Fonts/msyh.ttc"


_FONT_PATH = _find_chinese_font()


def put_chinese_text(
    img: np.ndarray,
    text: str,
    org: tuple,
    font_size: int = 18,
    color: tuple = (255, 255, 255),
    thickness: int = 1,
) -> None:
    """在 OpenCV BGR 图像上绘制中文文本（原地修改）。
    Args:
        img: BGR 图像 (H, W, 3), uint8
        text: 中文文本
        org: (x, y) 左下角坐标
        font_size: 字号
        color: BGR 颜色
        thickness: 预留参数（PIL 不支持描边粗细）
    """
    # BGR → RGB → PIL
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)

    try:
        font = ImageFont.truetype(_FONT_PATH, font_size)
    except Exception:
        font = ImageFont.load_default()

    # PIL 颜色是 RGB
    pil_color = (color[2], color[1], color[0])
    draw.text(org, text, font=font, fill=pil_color)

    # PIL → RGB → BGR，写回原数组
    img_rgb = np.array(pil_img)
    img[:, :, :] = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)


def put_chinese_text_with_bg(
    img: np.ndarray,
    text: str,
    org: tuple,
    font_size: int = 18,
    text_color: tuple = (255, 255, 255),
    bg_color: tuple = (0, 0, 0, 160),
) -> None:
    """绘制带半透明背景的中文文本。
    Args:
        img: BGR 图像 (H, W, 3), uint8
        text: 中文文本
        org: (x, y) 左上角坐标
        font_size: 字号
        text_color: 文本 BGR 颜色
        bg_color: 背景 RGBA 颜色（A 控制透明度）
    """
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb).convert("RGBA")

    try:
        font = ImageFont.truetype(_FONT_PATH, font_size)
    except Exception:
        font = ImageFont.load_default()

    # 测量文本大小
    temp_draw = ImageDraw.Draw(pil_img)
    bbox = temp_draw.textbbox(org, text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # 画背景
    overlay = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(
        [org[0] - 4, org[1] - 2, org[0] + text_w + 4, org[1] + text_h + 2],
        fill=bg_color,
    )
    pil_img = Image.alpha_composite(pil_img, overlay)

    # 画文本
    draw = ImageDraw.Draw(pil_img)
    pil_color = (text_color[2], text_color[1], text_color[0], 255)
    draw.text(org, text, font=font, fill=pil_color)

    # 转回 BGR
    img_rgb = np.array(pil_img.convert("RGB"))
    img[:, :, :] = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
