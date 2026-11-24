#!/bin/bash
# 启动创意桥（Mac）
cd "$(dirname "$0")" || exit 1
PY="$HOME/.zhipu-tools/venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "未找到依赖环境，请先跑 工具仓/zhipu-tools-oss/install.sh"
  read -n 1 -s -r -p "按任意键退出"
  exit 1
fi
echo "创意桥启动中，访问 http://127.0.0.1:8090/capabilities 查看能力"
$PY 创意桥.py
read -n 1 -s -r -p "服务已停止，按任意键关闭"