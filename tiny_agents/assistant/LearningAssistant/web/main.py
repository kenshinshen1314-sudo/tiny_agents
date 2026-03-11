"""
FastAPI 主应用入口
PDFParserAssistant Web 服务
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("PDFParserAssistant API 服务启动中...")
    yield
    logger.info("PDFParserAssistant API 服务关闭中...")


# 创建 FastAPI 应用
app = FastAPI(
    title="PDFParserAssistant API",
    description="智能文档解析助手 API - 提供文档加载、RAG问答、笔记管理和统计报告功能",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "PDFParserAssistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "tiny_agents.assistant.LearningAssistant.web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
