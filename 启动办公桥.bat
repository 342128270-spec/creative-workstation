@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PY=%USERPROFILE%\.zhipu-tools\venv\Scripts\python.exe"
if not exist "%PY%" (
  echo 缺依赖环境，先完成安装步骤
  pause & exit /b 1
)
echo 办公桥 http://127.0.0.1:8091
"%PY%" 办公桥.py
pause