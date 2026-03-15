"""旅行规划API路由"""

import asyncio
import json
import uuid
import threading
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner_agent import get_trip_planner_agent, ProgressCallback

router = APIRouter(prefix="/trip", tags=["旅行规划"])

# 存储每个请求的进度回调
_progress_callbacks = {}
_progress_lock = threading.Lock()


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
    """生成旅行计划"""
    try:
        print(f"\n{'='*60}")
        print(f"📥 收到旅行规划请求:")
        print(f"   城市: {request.city}")
        print(f"   日期: {request.start_date} - {request.end_date}")
        print(f"   天数: {request.travel_days}")
        print(f"{'='*60}\n")

        # 获取Agent实例
        print("🔄 获取多智能体系统实例...")
        agent = get_trip_planner_agent()

        # 生成旅行计划
        print("🚀 开始生成旅行计划...")
        trip_plan = agent.plan_trip(request)

        print("✅ 旅行计划生成成功,准备返回响应\n")

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan
        )

    except Exception as e:
        print(f"❌ 生成旅行计划失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.post(
    "/plan/stream",
    summary="生成旅行计划(流式进度)",
    description="使用SSE流式返回进度信息"
)
async def plan_trip_stream(request: TripRequest):
    """使用SSE流式生成旅行计划"""
    request_id = str(uuid.uuid4())

    # 创建进度回调
    progress_cb = ProgressCallback()
    latest_progress = {"progress": 0, "message": "准备中...", "step": 0}

    # 定义回调函数用于更新进度
    def on_progress(progress):
        nonlocal latest_progress
        latest_progress = progress
        progress["status"] = "running"
        print(f"   📊 进度: {progress.get('message', '')}")

    progress_cb.set_callback(on_progress)

    async def run_plan():
        """在异步上下文中运行计划"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: get_trip_planner_agent().plan_trip(request, progress_cb)
        )

    async def progress_generator():
        """SSE进度生成器"""
        nonlocal latest_progress

        # 启动任务
        task = asyncio.create_task(run_plan())

        # 持续推送进度直到完成
        while not task.done():
            await asyncio.sleep(0.3)
            # 每次都推送最新进度
            yield f"data: {json.dumps(latest_progress, ensure_ascii=False)}\n\n"

        # 任务完成，获取结果
        try:
            result = await task
            # 发送完成消息
            final_progress = progress_cb.get_progress()
            final_progress["status"] = "completed"
            final_progress["message"] = "✅ 旅行计划生成完成!"
            yield f"data: {json.dumps(final_progress, ensure_ascii=False)}\n\n"
            # 发送完整数据
            yield f"data: {json.dumps({'type': 'result', 'success': True, 'data': result.model_dump()}, ensure_ascii=False)}\n\n"
        except Exception as e:
            error_progress = {
                "step": 0,
                "progress": 0,
                "message": f"生成失败: {str(e)}",
                "status": "error"
            }
            yield f"data: {json.dumps(error_progress, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        progress_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get(
    "/health",
    summary="健康检查"
)
async def health_check():
    """健康检查"""
    try:
        agent = get_trip_planner_agent()
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_name": agent.agent.name,
            "tools_count": len(agent.agent.list_tools())
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"服务不可用: {str(e)}")
