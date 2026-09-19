"""火龙果 AI 视觉监控系统 — 便捷入口点

用法:
    python dragon_fruit_monitor.py --source image.jpg
    python dragon_fruit_monitor.py --source ./images/ --output results/
    python dragon_fruit_monitor.py --serve --port 5000
"""

from dragon_fruit.cli import main

if __name__ == "__main__":
    main()
