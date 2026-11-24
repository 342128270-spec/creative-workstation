@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PY=%USERPROFILE%\.zhipu-tools\venv\Scripts\python.exe"
if not exist "%PY%" (
  echo 未找到依赖环境，请先运行 zhipu-tools-oss\install.sh 对应步骤
  pause
  exit /b 1
)
echo 创意桥启动中，访问 http://127.0.0.1:8090/capabilities
"%PY%" 创意桥.py
pause