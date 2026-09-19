"""命令行入口 — 火龙果 AI 监控系统"""

import argparse
import sys
from pathlib import Path

from dragon_fruit.config import MonitoringConfig
from dragon_fruit.pipeline.orchestrator import DragonFruitMonitor


def main():
    parser = argparse.ArgumentParser(
        description="火龙果 AI 视觉监控系统 — 成熟度检测、病虫害识别、生长异常分析"
    )
    parser.add_argument("--source", default=None,
                        help="输入图像路径或目录（Web 模式时可选）")
    parser.add_argument("--output", default=None,
                        help="输出目录（默认: runs/dragon_fruit）")
    parser.add_argument("--weights", default=None,
                        help="成熟度检测模型路径（默认: exp4/best.pt）")
    parser.add_argument("--pest-weights", default=None,
                        help="病虫害分类模型路径（可选）")
    parser.add_argument("--conf-thres", type=float, default=0.25,
                        help="检测置信度阈值（默认: 0.25）")
    parser.add_argument("--no-pest", action="store_true",
                        help="禁用病虫害检测")
    parser.add_argument("--no-growth", action="store_true",
                        help="禁用生长异常检测")
    parser.add_argument("--no-preprocess", action="store_true",
                        help="禁用图像预处理")
    parser.add_argument("--serve", action="store_true",
                        help="启动 Gradio Web 界面（生成公网链接）")
    parser.add_argument("--port", type=int, default=5000,
                        help="Web 服务端口（默认: 5000）")
    parser.add_argument("--no-share", action="store_true",
                        help="不生成公网链接（仅本地访问）")

    args = parser.parse_args()

    # Web 模式（Gradio 界面，支持公网链接）
    if args.serve:
        from dragon_fruit.web.app import run_server
        run_server(port=args.port, share=not args.no_share)
        return

    if not args.source:
        print("错误: 请指定 --source 或使用 --serve 启动 Web 界面")
        sys.exit(1)

    # 构建配置
    config = MonitoringConfig()
    if args.weights:
        config.weights = Path(args.weights)
    if args.pest_weights:
        config.pest_weights = Path(args.pest_weights)
    if args.output:
        config.output_dir = Path(args.output)
        config.log_dir = Path(args.output) / "logs"
    else:
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        config.output_dir = config.output_dir / ts
        config.log_dir = config.output_dir / "logs"
    config.conf_thres = args.conf_thres
    config.enable_pest = not args.no_pest
    config.enable_growth = not args.no_growth
    config.enable_preprocess = not args.no_preprocess

    # 运行
    source = Path(args.source)
    monitor = DragonFruitMonitor(config)

    if source.is_dir():
        print(f"批量处理目录: {source}")
        results = monitor.process_directory(source)
        print(f"\n处理完成，共 {len(results)} 张图像。")
        print(f"结果保存在: {config.output_dir}")
    elif source.is_file():
        result = monitor.process_and_save(source)
        print(f"摘要: {result.summary}")
        print(f"标注图像: {result.annotated_image_path}")
        if result.alerts:
            print("预警:")
            for a in result.alerts:
                print(f"  [{a.level.value}] {a.message}")
        print(f"日志目录: {config.log_dir}")
    else:
        print(f"错误: 源路径不存在: {source}")
        sys.exit(1)


if __name__ == "__main__":
    main()
