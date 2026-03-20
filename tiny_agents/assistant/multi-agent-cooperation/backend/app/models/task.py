from enum import Enum
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    TEAM_BUILDING = "team_building"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class TaskType(str, Enum):
    DEV = "dev"
    WRITING = "writing"

class TaskComplexity(str, Enum):
    SIMPLE = "simple"
    NORMAL = "normal"
    COMPLEX = "complex"

class Task(BaseModel):
    id: str
    user_input: str
    task_type: Optional[TaskType] = None
    complexity: Optional[TaskComplexity] = None
    status: TaskStatus = TaskStatus.PENDING
    template_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    progress: int = 0
    cost: float = 0.0
    metadata: Dict[str, Any] = {}

class TaskCreate(BaseModel):
    user_input: str

class TaskResponse(BaseModel):
    id: str
    status: TaskStatus
    progress: int
    message: Optional[str] = None