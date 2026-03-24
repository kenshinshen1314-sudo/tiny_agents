#!/bin/bash

# 后端一键启动脚本
# 默认端口: 8080

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="/Users/kenshin/Projects/my-first-agent"

echo "🚀 启动后端服务 (端口 8080)..."

# 设置 PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 使用 deep_research 的虚拟环境
source "$SCRIPT_DIR/../../deep_research/backend/.venv/bin/activate"

cd "$SCRIPT_DIR/../../multiagent-content-gen-platform/backend"

python -m src.main
