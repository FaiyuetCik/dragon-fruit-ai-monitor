"""火龙果 AI 视觉监控系统"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# PyTorch 2.6+ 默认 weights_only=True，YOLOv5 checkpoint 不兼容
# 在导入任何 YOLOv5 模块之前修补 torch.load 默认值
import torch
_original_load = torch.load

def _patched_load(*args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _original_load(*args, **kwargs)

torch.load = _patched_load
