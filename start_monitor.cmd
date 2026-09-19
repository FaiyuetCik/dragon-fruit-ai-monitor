@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "PYTHONNOUSERSITE=1"
set "PYTHONUTF8=1"
set "PYTHONPATH="
set "PYTHONHOME="
set "NO_PROXY=localhost,127.0.0.1,%NO_PROXY%"
set "GRADIO_ANALYTICS_ENABLED=False"
set "YOLOv5_AUTOINSTALL=False"
set "YOLO_CONFIG_DIR=%~dp0.venv\runtime\ultralytics"
if not exist "%YOLO_CONFIG_DIR%" mkdir "%YOLO_CONFIG_DIR%"
if not exist ".venv\Scripts\python.exe" (
  echo Missing project environment. See ENVIRONMENT.md.
  pause
  exit /b 1
)
if "%~1"=="" (
  echo Open http://127.0.0.1:7860 after the server starts.
  echo Press Ctrl+C to stop.
  ".venv\Scripts\python.exe" dragon_fruit_monitor.py --serve --no-share --port 7860
  pause
) else (
  ".venv\Scripts\python.exe" dragon_fruit_monitor.py %*
  exit /b !errorlevel!
)