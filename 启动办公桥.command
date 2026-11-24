#!/bin/bash
cd "$(dirname "$0")" || exit 1
PY="$HOME/.zhipu-tools/venv/bin/python"
[ -x "$PY" ] || { echo "缺依赖环境，先跑 zhipu-tools-oss/install.sh"; read -n1 -s; exit 1; }
echo "办公桥 -> http://127.0.0.1:8091"
"$PY" 办公桥.py
read -n 1 -s -r -p "已停止，按任意键关闭"