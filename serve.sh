#!/usr/bin/env bash
# ============================================================
#  非遗志 · HeritageWiki 本地预览脚本（Git Bash / macOS / Linux）
#  首次运行自动创建虚拟环境并安装依赖
# ============================================================
set -e
cd "$(dirname "$0")"

if [ ! -f ".venv/Scripts/python.exe" ] && [ ! -f ".venv/bin/python" ]; then
  echo "[非遗志] 正在创建虚拟环境..."
  python -m venv .venv
  PIP=".venv/Scripts/python.exe"
  [ -f "$PIP" ] || PIP=".venv/bin/python"
  "$PIP" -m pip install --upgrade pip -q -i https://pypi.tuna.tsinghua.edu.cn/simple
  "$PIP" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

PY=".venv/Scripts/python.exe"
[ -f "$PY" ] || PY=".venv/bin/python"

echo "[非遗志] 本地预览：http://127.0.0.1:8000 （Ctrl+C 停止）"
exec "$PY" -m mkdocs serve --dev-addr 127.0.0.1:8000
