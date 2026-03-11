@echo off
REM PDFParserAssistant Web 服务启动脚本 (Windows)

echo ==========================================
echo   PDFParserAssistant Web 服务启动
echo ==========================================

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..\..

echo 项目根目录: %PROJECT_ROOT%

REM 检查并安装 Python 依赖
echo.
echo 检查依赖...

python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [安装 FastAPI 依赖...]
    cd %PROJECT_ROOT%\..\..
    pip install -r requirements.txt
) else (
    echo [OK] Python 依赖已安装
)

REM 检查并安装 Node 依赖
if not exist "%SCRIPT_DIR%web-frontend\node_modules" (
    echo [安装前端依赖...]
    cd "%SCRIPT_DIR%web-frontend"
    call npm install
) else (
    echo [OK] 前端依赖已安装
)

echo.
echo ==========================================
echo   启动服务
echo ==========================================
echo.
echo 后端服务: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo 前端服务: http://localhost:5173
echo.

REM 在新窗口启动后端
start "PDFParserAssistant Backend" cmd /k "cd /d %PROJECT_ROOT%\..\.. && uvicorn tiny_agents.assistant.web.main:app --reload --host 0.0.0.0 --port 8000"

REM 等待后端启动
timeout /t 2 /nobreak >nul

REM 启动前端
cd "%SCRIPT_DIR%web-frontend"
call npm run dev

pause
