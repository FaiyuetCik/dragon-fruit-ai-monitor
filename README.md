# 火龙果 AI 视觉监测系统

基于 YOLOv5、OpenCV 和 Gradio 的火龙果图像分析项目。支持识别图片中的成熟与未成熟果实、统计数量，并输出标注图片、分析报告和预警记录。

[English](README.en.md) · [环境配置](ENVIRONMENT.md) · [数据准备](dragon_fruit/data/README.md)

> 一个基于 YOLOv5 的火龙果成熟度图像分析系统源码和演示框架，支持本地图片识别、批量处理、结果报告和基础异常提示。源码功能链路可以在本地运行，但模型权重和训练数据不随仓库公开；用户需要自行提供兼容的 `best.pt` 和待分析图片。

> 当前版本面向单张图片和图片目录的分析与演示。实时摄像头监测尚未接入；病虫害分类接口已实现，但仓库未提供病虫害模型。

## 功能与当前状态

| 模块 | 当前能力 |
| --- | --- |
| 成熟度识别 | 基于自训练 YOLOv5 模型输出果实位置、成熟/未成熟类别及置信度，需要单独准备模型权重 |
| 图像预处理 | 亮度和对比度调整、CLAHE 增强、降噪及尺寸归一化 |
| 生长异常分析 | 基于 HSV 颜色与边缘直线计算绿化率、黄化率和倾斜角，属于待实地验证的规则分析 |
| 网页界面 | 上传单张图片，查看检测结果、分析表格和预警，下载 JSON 与标注图 |
| 批量处理 | 通过命令行分析一个目录的图片，生成逐图结果及汇总报告 |
| 预警记录 | 根据规则生成提示并保存 CSV 日志，尚未实现外部消息推送 |
| 病虫害分类 | 预留 Healthy、Aphids、Anthracnose 分类接口；未配置权重时跳过，不能据此判断无病虫害 |
| 实时监控 | 尚未接入自定义监测流程 |

界面当前使用英文标签。核心应用代码位于 [dragon_fruit/](dragon_fruit/)，根目录及 models、utils 等目录保留 YOLOv5 基础代码。

## 下载后需要准备什么

本仓库发布源码、配置和环境依赖清单。**训练权重、原始图片、运行记录和虚拟环境未上传，因此仅克隆仓库不能直接完成识别。**

1. 准备针对本项目两类火龙果训练的 YOLOv5 权重，类别顺序为 `shenghlg`（未成熟）、`huolongguo`（成熟）。
2. 网页默认加载 `runs/train/exp4/weights/best.pt`，请在本地创建目录并放入对应权重；也可修改 [MonitoringConfig.weights](dragon_fruit/config.py)。
3. 自行准备待识别图片。命令行可用 `--weights` 指定其他权重路径。
4. 如需训练，补齐 `yolo_dataset/images/train/` 和 `yolo_dataset/images/val/`，使图片文件名与对应标签匹配。

通用的 `yolov5s.pt` 不能替代本项目的火龙果成熟度模型。仓库当前未提供火龙果权重的公开下载地址。

## 快速开始（Windows / Python 3.12 / CPU）

在安装 Python 3.12 和 Git 后，打开 PowerShell：

```powershell
git clone https://github.com/FaiyuetCik/dragon-fruit-ai-monitor.git
cd dragon-fruit-ai-monitor
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install "torch==2.6.0+cpu" "torchvision==0.21.0+cpu" --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements-monitor.lock.txt
.\.venv\Scripts\python.exe -m pip check
```

如果没有 `py` 启动器，请将 `py -3.12` 替换为你的 Python 3.12 解释器。依赖固定为经过本地验证的版本，包括 NumPy 1.26.4 和 Gradio 4.44.1。更多说明见 [ENVIRONMENT.md](ENVIRONMENT.md)。

### 网页识别

完成环境安装并放置默认模型权重后，双击 `start_monitor.cmd`，或执行：

```powershell
.\start_monitor.cmd
```

打开 http://127.0.0.1:7860，上传图片并点击 **Analyze**。启动脚本默认仅在本机提供服务，按 Ctrl+C 停止。

注意：当前 `--serve` 分支不会应用命令行中的 `--weights`、`--pest-weights` 等分析配置；网页模型应通过默认文件位置或 [config.py](dragon_fruit/config.py) 配置。

### 命令行识别

先将你自己的图片放入 `input/` 目录；下列文件名是示例：

```powershell
# 分析单张图片
.\start_monitor.cmd --source input/fruit.jpg --output runs/example

# 批量分析一个目录
.\start_monitor.cmd --source input --output runs/batch

# 指定火龙果权重及检测阈值
.\start_monitor.cmd --source input/fruit.jpg --weights models/local-best.pt --conf-thres 0.5

# 关闭病虫害与生长异常模块，仅查看成熟度识别
.\start_monitor.cmd --source input/fruit.jpg --no-pest --no-growth
```

## 输出结果

指定输出目录后，程序会生成：

- `<图片名>_annotated.jpg`：带检测框与分析信息的标注图片。
- `<图片名>_result.json`：该图片的检测结果、异常指标、预警和摘要。
- `batch_report.json`：目录批处理的汇总结果。
- `logs/alerts_<日期>.csv`：预警日志。

未指定 `--output` 时，命令行结果默认存入 `runs/dragon_fruit/<时间戳>/`；网页结果存入 `runs/dragon_fruit/web/`。

## 项目结构

```text
dragon_fruit_monitor.py        命令行入口
dragon_fruit/
  config.py                   模型路径、阈值和模块开关
  preprocessing/              图像增强和预处理
  detection/                  成熟度识别
  classification/             病虫害分类接口
  growth/                     颜色与几何异常分析
  pipeline/                   流程编排、预警和报告
  web/                        Gradio 界面
  data/                       数据增强与训练辅助脚本
yolo_dataset/
  K.yaml                      两类火龙果的数据配置
  labels/                     YOLO 格式标注
models/、utils/               YOLOv5 基础模块
start_monitor.cmd             独立环境启动入口
requirements-monitor.lock.txt 完整依赖版本清单
verify_monitor_environment.py 本地端到端验证脚本
```

## 验证与局限

2026-09-19 的本地环境验证完成了 7 张图片的批处理，以及网页上传、识别和文件下载。验证脚本依赖本地权重与原有 7 张测试图片（含 `yolo_dataset/images/test/1.png`）；这些资源未发布，刚克隆的仓库无法直接复现该验证。

准备好这些本地资源后，可运行：

```powershell
.\.venv\Scripts\python.exe verify_monitor_environment.py
```

验证成功时会生成 `runs/environment-check/<时间>/verification.json`。这项验证只检查运行流程，不代表实际果园中的识别准确率。

已知局限：

- 数据规模较小，尚需在不同光照、遮挡、背景和拍摄距离下进行独立评测。
- 生长异常指标受背景影响，不能直接作为植株健康诊断。
- 病虫害模型未就绪；实时摄像头、历史趋势看板和外部告警推送仍待完成。
- “无成熟果实”规则目前仅在完全未检测到果实时触发，尚需区分“只有未成熟果实”的情况。

## 来源与许可证

本项目包含并基于 [Ultralytics YOLOv5](https://github.com/ultralytics/yolov5) 源码，统一采用 GNU AGPL v3。`dragon_fruit/` 是本项目的原创应用层和修改集成代码。详细归属、第三方依赖说明和无担保声明见 [NOTICE](NOTICE)；许可证文本见 [LICENSE](LICENSE)。
