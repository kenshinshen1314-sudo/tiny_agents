"""
FastAPI 路由定义
提供文档加载、RAG问答、笔记管理和统计报告的 API 接口
"""

import asyncio
import os
import uuid
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .manager import get_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["PDFParserAssistant"])

# 上传文件保存目录
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ========================
# 请求模型定义
# ========================

class InitRequest(BaseModel):
    """初始化助手请求"""
    user_id: str = Field(..., description="用户ID")


class DocumentLoadRequest(BaseModel):
    """加载文档请求"""
    user_id: str = Field(..., description="用户ID")
    file_path: str = Field(..., description="PDF文件路径")


class ChatRequest(BaseModel):
    """问答请求"""
    user_id: str = Field(..., description="用户ID")
    question: str = Field(..., description="问题")
    use_advanced_search: bool = Field(default=True, description="是否使用高级搜索")


class NoteRequest(BaseModel):
    """添加笔记请求"""
    user_id: str = Field(..., description="用户ID")
    content: str = Field(..., description="笔记内容")
    concept: Optional[str] = Field(default=None, description="相关概念")


class ReportRequest(BaseModel):
    """生成报告请求"""
    user_id: str = Field(..., description="用户ID")


class RecallRequest(BaseModel):
    """回忆请求"""
    user_id: str = Field(..., description="用户ID")
    query: str = Field(..., description="查询关键词")
    limit: int = Field(default=5, description="返回条数")


# ========================
# API 端点
# ========================

@router.post("/init")
async def init_assistant(request: InitRequest):
    """
    初始化助手

    为指定用户创建或获取 PDFParserAssistant 实例
    """
    try:
        manager = get_manager()
        assistant = await manager.get_or_create(request.user_id)

        return JSONResponse({
            "success": True,
            "session_id": assistant.session_id,
            "user_id": assistant.user_id,
            "message": "助手初始化成功"
        })
    except Exception as e:
        logger.error(f"初始化助手失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    上传 PDF 文件

    接收用户上传的 PDF 文件并保存到临时目录
    """
    try:
        # 验证文件类型
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持上传 PDF 文件")

        # 生成唯一文件名
        file_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # 保存文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"文件上传成功: {file.filename} -> {file_path}")

        return JSONResponse({
            "success": True,
            "file_path": file_path,
            "filename": file.filename,
            "size": len(content),
            "message": "文件上传成功"
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/document/load")
async def load_document(request: DocumentLoadRequest):
    """
    加载文档到知识库

    将上传的 PDF 文档加载到 RAG 知识库
    """
    try:
        manager = get_manager()
        assistant = await manager.get(request.user_id)

        if assistant is None:
            raise HTTPException(status_code=404, detail="助手未初始化，请先调用 /api/init")

        # 验证文件存在
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"文件不存在: {request.file_path}")

        # 记录开始时间
        logger.info(f"开始加载文档: {request.file_path}")
        start_time = datetime.now()

        # 在线程池中执行耗时操作
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            assistant.load_document,
            request.file_path
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"文档加载完成，耗时 {duration:.2f} 秒")

        if result.get("success"):
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=400, detail=result.get("message"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"加载文档失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    智能问答

    向文档助手提问并获取基于 RAG 的回答
    """
    try:
        manager = get_manager()
        assistant = await manager.get(request.user_id)

        if assistant is None:
            raise HTTPException(status_code=404, detail="助手未初始化，请先调用 /api/init")

        start_time = datetime.now()

        # 在线程池中执行问答操作
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(
            None,
            assistant.ask,
            request.question,
            request.use_advanced_search
        )

        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        return JSONResponse({
            "answer": answer,
            "duration_ms": duration_ms,
            "timestamp": end_time.isoformat()
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"问答失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notes")
async def add_note(request: NoteRequest):
    """
    添加学习笔记

    将学习笔记保存到语义记忆中
    """
    try:
        manager = get_manager()
        assistant = await manager.get(request.user_id)

        if assistant is None:
            raise HTTPException(status_code=404, detail="助手未初始化，请先调用 /api/init")

        assistant.add_note(request.content, request.concept)

        return JSONResponse({
            "success": True,
            "message": "笔记已保存",
            "concept": request.concept or "general"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加笔记失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recall")
async def recall(request: RecallRequest):
    """
    回忆相关信息

    从记忆中检索相关信息
    """
    try:
        manager = get_manager()
        assistant = await manager.get(request.user_id)

        if assistant is None:
            raise HTTPException(status_code=404, detail="助手未初始化，请先调用 /api/init")

        result = assistant.recall(request.query, request.limit)

        return JSONResponse({
            "result": result,
            "query": request.query
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"回忆失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats(user_id: str):
    """
    获取统计信息

    获取当前会话的学习统计信息
    """
    try:
        manager = get_manager()
        assistant = await manager.get(user_id)

        if assistant is None:
            raise HTTPException(status_code=404, detail="助手未初始化，请先调用 /api/init")

        stats = assistant.get_stats()

        return JSONResponse(stats)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report")
async def generate_report(request: ReportRequest):
    """
    生成学习报告

    生成包含学习指标、记忆摘要和 RAG 状态的完整报告
    """
    try:
        manager = get_manager()
        assistant = await manager.get(request.user_id)

        if assistant is None:
            raise HTTPException(status_code=404, detail="助手未初始化，请先调用 /api/init")

        # 在线程池中执行报告生成
        loop = asyncio.get_event_loop()
        report = await loop.run_in_executor(
            None,
            assistant.generate_report,
            True
        )

        return JSONResponse({
            "success": True,
            "report": report,
            "message": "报告生成成功"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    健康检查

    检查 API 服务是否正常运行
    """
    return JSONResponse({
        "status": "healthy",
        "service": "PDFParserAssistant API",
        "timestamp": datetime.now().isoformat()
    })
