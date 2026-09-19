# 火龙果监测系统：独立运行环境

## 启动

双击项目根目录的 `start_monitor.cmd`，等待显示服务地址后，在浏览器打开：

http://127.0.0.1:7860

关闭服务：在启动窗口按 Ctrl+C。默认只在本机提供服务，不生成公网分享链接。

在 PowerShell 中批量识别：

```powershell
Set-Location <project-root>
.\start_monitor.cmd --source yolo_dataset/images/test --output runs/my-batch
```

## 专用解释器

`.venv\Scripts\python.exe`

在 PyCharm / VS Code 中把项目解释器设置为上面的路径。不要用 Anaconda base 环境的 `python` 启动本项目。

环境使用 Python 3.12、CPU 版 PyTorch 2.6.0 / torchvision 0.21.0、NumPy 1.26.4、OpenCV 4.11.0.86 和 Gradio 4.44.1。独立环境不继承全局 site-packages。此环境用于现有模型推理与网页演示，不包含 CUDA。

`requirements-monitor.txt` 固定主要依赖；`requirements-monitor.lock.txt` 记录验证后的全部安装版本。原 `requirements.txt` 是 YOLOv5 通用依赖清单，不应用于覆盖这个已验证环境。

## 重建环境

在项目目录中执行（联网下载依赖；需要 Python 3.12）：

```powershell
& 'python3.12.exe' -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install 'torch==2.6.0+cpu' 'torchvision==0.21.0+cpu' --index-url https://download.pytorch.org/whl/cpu
& '.\.venv\Scripts\python.exe' -m pip install -r requirements-monitor.lock.txt
& '.\.venv\Scripts\python.exe' -m pip check
```

在新电脑上，需要把第一行的 Python 路径替换为该电脑的 Python 3.12 解释器。如果尚未生成 lock 文件，则第三行使用 `requirements-monitor.txt`。

## 验证

```powershell
& '.\.venv\Scripts\python.exe' verify_monitor_environment.py
```

验证脚本会检查依赖、处理 7 张现有测试图片，并临时在本机 17860 端口启动网页服务，通过真实 Gradio API 上传图片、检查输出图像和下载文件；结束后自动关闭测试服务。端口 17860 应保持空闲。

结果保存在 `runs/environment-check/<时间>/verification.json`，只有所有检查通过才会生成 PASS 记录。这是环境和功能流程验证，不是检测准确率评测。

## 功能边界

恢复环境不会补齐病虫害模型、摄像头监控或修正业务规则。未配置病虫害权重时，原有程序仍会跳过该模块。

## 验证记录（2026-09-19）

首次完整验证通过：7 张图片全部生成报告和标注图，共检测出 13 个果实；网页 HTTP 返回 200，上传识别和文件下载通过。此结果不代表准确率评测。

首次验证时 Ultralytics 自动将用户级 settings.json 重置为默认值，原自定义配置未能保留副本。现启动与验证脚本已将 Ultralytics 配置隔离到 .venv/runtime/ultralytics，后续不再共用用户级配置。Anaconda base 的依赖未修改。
