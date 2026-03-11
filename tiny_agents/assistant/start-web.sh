#!/bin/bash
# PDFParserAssistant Web 服务启动脚本

echo "=========================================="
echo "  PDFParserAssistant Web 服务启动"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "项目根目录: $PROJECT_ROOT"

# 检查是否安装了依赖
echo ""
echo "检查依赖..."

# 检查 Python 依赖
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ FastAPI 未安装，正在安装..."
    cd "$PROJECT_ROOT/../.."
    pip install -r requirements.txt
else
    echo "✅ Python 依赖已安装"
fi

# 检查 Node 依赖
if [ ! -d "$SCRIPT_DIR/web-frontend/node_modules" ]; then
    echo "❌ 前端依赖未安装，正在安装..."
    cd "$SCRIPT_DIR/web-frontend"
    npm install
else
    echo "✅ 前端依赖已安装"
fi

echo ""
echo "=========================================="
echo "  启动服务"
echo "=========================================="
echo ""
echo "后端服务: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo "前端服务: http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动后端（在后台）
cd "$PROJECT_ROOT/../.."
uvicorn tiny_agents.assistant.web.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 启动前端
cd "$SCRIPT_DIR/web-frontend"
npm run dev

# 清理：当前端停止时，也停止后端
kill $BACKEND_PID
