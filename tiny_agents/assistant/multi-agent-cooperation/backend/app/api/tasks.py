from fastapi import APIRouter, HTTPException
from app.models.task import Task, TaskCreate, TaskResponse, TaskStatus
from app.services.task_service import TaskService
from typing import List
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
task_service = TaskService()

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    task_id = str(uuid.uuid4())
    new_task = Task(
        id=task_id,
        user_input=task.user_input,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    return await task_service.create_task(new_task)

@router.get("/", response_model=List[TaskResponse])
async def list_tasks():
    return await task_service.list_tasks()

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/{task_id}/start")
async def start_task(task_id: str):
    result = await task_service.start_task(task_id)
    return result

@router.post("/{task_id}/pause")
async def pause_task(task_id: str):
    return await task_service.pause_task(task_id)

@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    return await task_service.cancel_task(task_id)