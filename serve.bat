@echo off
rem ============================================================
rem  非遗志 · HeritageWiki 本地预览脚本
rem  双击运行，或在 VSCode 终端执行本文件
rem  首次运行会自动创建虚拟环境并安装依赖（使用国内镜像）
rem ============================================================
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [非遗志] 正在创建虚拟环境...
  where py >nul 2>nul && (py -3 -m venv .venv) || (python -m venv .venv)
  echo [非遗志] 正在安装依赖（清华镜像）...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip -q -i https://pypi.tuna.tsinghua.edu.cn/simple
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo.
echo [非遗志] 启动本地预览：http://127.0.0.1:8000
echo [非遗志] 修改 docs/ 下的 Markdown 后浏览器会自动刷新；按 Ctrl+C 停止服务。
echo.
".venv\Scripts\python.exe" -m mkdocs serve --dev-addr 127.0.0.1:8000
pause
