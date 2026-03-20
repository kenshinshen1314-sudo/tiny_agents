from app.models.task import Task, TaskResponse, TaskStatus
from typing import List, Dict, Any

class TaskService:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    async def create_task(self, task: Task) -> TaskResponse:
        self.tasks[task.id] = task
        return TaskResponse(
            id=task.id,
            status=task.status,
            progress=task.progress,
            message="任务创建成功"
        )

    async def get_task(self, task_id: str) -> TaskResponse:
        task = self.tasks.get(task_id)
        if not task:
            return None
        return TaskResponse(
            id=task.id,
            status=task.status,
            progress=task.progress
        )

    async def list_tasks(self) -> List[TaskResponse]:
        return [
            TaskResponse(id=t.id, status=t.status, progress=t.progress)
            for t in self.tasks.values()
        ]

    async def start_task(self, task_id: str) -> Dict[str, Any]:
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}
        task.status = TaskStatus.ANALYZING
        return {"message": "任务已开始", "task_id": task_id}

    async def pause_task(self, task_id: str) -> Dict[str, Any]:
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}
        task.status = TaskStatus.PAUSED
        return {"message": "任务已暂停"}

    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}
        task.status = TaskStatus.FAILED
        return {"message": "任务已取消"}