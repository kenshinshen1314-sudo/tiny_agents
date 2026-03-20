from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class RoleStatus(str, Enum):
    IDLE = "idle"
    WAITING = "waiting"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"

class Role(BaseModel):
    name: str
    status: RoleStatus = RoleStatus.IDLE
    output: Optional[Any] = None
    dependencies: List[str] = []

class TeamTemplate(BaseModel):
    id: str
    name: str
    description: str
    task_type: str
    roles: List[str]
    execution_flow: List[Dict[str, Any]]

class Team(BaseModel):
    task_id: str
    template_id: str
    roles: List[Role]
    status: str = "building"