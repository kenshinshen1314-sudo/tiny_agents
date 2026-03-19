# 多Agent协作团队系统实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个前后端分离的多Agent协作团队系统，前端使用Vue+TypeScript，后端基于tiny_agents框架

**Architecture:** 采用分层架构，后端分为API层、服务层、Agent层；前端分为视图层、状态管理层、API通信层

**Tech Stack:**
- 后端: Python 3.12+, FastAPI, tiny_agents框架
- 前端: Vue 3 + TypeScript + Vite + Axios + Pinia
- 数据库: SQLite (开发) / PostgreSQL (生产)

---

## 项目结构

```
assistant/multi-agent-cooperation/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI主应用
│   │   ├── config.py          # 配置
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── task.py        # 任务模型
│   │   │   ├── team.py        # 团队模型
│   │   │   └── message.py     # 消息模型
│   │   ├── api/               # API路由
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py       # 任务相关API
│   │   │   ├── teams.py       # 团队相关API
│   │   │   └── templates.py   # 模板相关API
│   │   ├── services/          # 业务服务
│   │   │   ├── __init__.py
│   │   │   ├── task_service.py
│   │   │   ├── team_service.py
│   │   │   └── template_service.py
│   │   └── agents/            # Agent核心模块
│   │       ├── __init__.py
│   │       ├── team_manager.py    # TeamManager
│   │       ├── team_leader.py     # TeamLeader
│   │       ├── agent_factory.py   # AgentFactory
│   │       ├── templates/         # 团队模板
│   │       │   ├── __init__.py
│   │       │   ├── dev_team.py   # 软件开发团队
│   │       │   └── writing_team.py # 内容创作团队
│   │       └── roles/             # 角色定义
│   │           ├── __init__.py
│   │           ├── base.py        # 基础角色
│   │           ├── pm.py          # ProductManager
│   │           ├── architect.py   # 架构师
│   │           ├── developer.py    # 开发人员
│   │           ├── writer.py       # 作家
│   │           └── editor.py       # 编辑
│   ├── requirements.txt
│   └── run.py
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── api/
│   │   │   ├── index.ts       # Axios配置
│   │   │   ├── tasks.ts      # 任务API
│   │   │   ├── teams.ts      # 团队API
│   │   │   └── templates.ts  # 模板API
│   │   ├── components/
│   │   │   ├── TaskInput.vue     # 任务输入组件
│   │   │   ├── TemplateSelect.vue # 模板选择组件
│   │   │   ├── TaskProgress.vue  # 任务进度组件
│   │   │   ├── AgentCard.vue     # Agent卡片组件
│   │   │   └── ResultDisplay.vue # 结果展示组件
│   │   ├── views/
│   │   │   ├── HomeView.vue      # 首页/任务输入
│   │   │   ├── TaskView.vue      # 任务详情/进度
│   │   │   └── ResultView.vue    # 结果展示
│   │   ├── stores/
│   │   │   ├── task.ts       # 任务状态管理
│   │   │   └── team.ts       # 团队状态管理
│   │   ├── types/
│   │   │   └── index.ts      # TypeScript类型定义
│   │   ├── router/
│   │   │   └── index.ts      # 路由配置
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
└── README.md
```

---

## Chunk 1: 项目初始化与后端基础框架

### Task 1: 初始化后端项目结构

**Files:**
- Create: `assistant/multi-agent-cooperation/backend/app/__init__.py`
- Create: `assistant/multi-agent-cooperation/backend/app/config.py`
- Create: `assistant/multi-agent-cooperation/backend/requirements.txt`

- [ ] **Step 1: 创建requirements.txt**

```txt
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
python-multipart==0.0.6
tiny_agents @ file:///Users/kenshin/Projects/my-first-agent/tiny_agents
```

- [ ] **Step 2: 创建配置模块**

```python
# assistant/multi-agent-cooperation/backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Multi-Agent Cooperation"
    debug: bool = True

    # LLM配置
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-20250514"

    # 并发控制
    max_concurrent_tasks: int = 10
    max_agents_per_task: int = 5

    # 实例池配置
    agent_pool_max_size: int = 5
    agent_pool_timeout: int = 1800  # 30分钟

    # 数据目录
    data_dir: str = "./data"
    tasks_dir: str = "./data/tasks"

    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 3: 创建目录结构**

```bash
cd assistant/multi-agent-cooperation/backend
mkdir -p app/models app/api app/services app/agents/templates app/agents/roles
```

- [ ] **Step 4: Commit**

```bash
git add assistant/multi-agent-cooperation/backend/
git commit -m "chore: 初始化后端项目结构"
```

### Task 2: 创建FastAPI主应用

**Files:**
- Create: `assistant/multi-agent-cooperation/backend/app/main.py`
- Create: `assistant/multi-agent-cooperation/backend/run.py`

- [ ] **Step 1: 创建FastAPI主应用**

```python
# assistant/multi-agent-cooperation/backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Multi-Agent Cooperation API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

- [ ] **Step 2: 创建运行脚本**

```python
# assistant/multi-agent-cooperation/backend/run.py
import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
```

- [ ] **Step 3: 测试后端启动**

```bash
cd assistant/multi-agent-cooperation/backend
pip install -r requirements.txt
python run.py
# 验证: curl http://localhost:8000/health
```

- [ ] **Step 4: Commit**

```bash
git add assistant/multi-agent-cooperation/backend/
git commit -m "feat: 创建FastAPI主应用"
```

### Task 3: 初始化前端项目

**Files:**
- Create: `assistant/multi-agent-cooperation/frontend/package.json`
- Create: `assistant/multi-agent-cooperation/frontend/vite.config.ts`
- Create: `assistant/multi-agent-cooperation/frontend/tsconfig.json`

- [ ] **Step 1: 创建package.json**

```json
{
  "name": "multi-agent-cooperation-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.5",
    "element-plus": "^2.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vue-tsc": "^1.8.0"
  }
}
```

- [ ] **Step 2: 创建vite.config.ts**

```typescript
// assistant/multi-agent-cooperation/frontend/vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

- [ ] **Step 3: 创建tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 4: 创建前端入口文件**

```html
<!-- assistant/multi-agent-cooperation/frontend/index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>多Agent协作系统</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 5: 创建main.ts和App.vue**

```typescript
// assistant/multi-agent-cooperation/frontend/src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

```vue
<!-- assistant/multi-agent-cooperation/frontend/src/App.vue -->
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
  background: #f5f7fa;
}
</style>
```

- [ ] **Step 6: 安装依赖并测试**

```bash
cd assistant/multi-agent-cooperation/frontend
npm install
npm run dev
```

- [ ] **Step 7: Commit**

```bash
git add assistant/multi-agent-cooperation/
git commit -m "chore: 初始化前端项目"
```

---

## Chunk 2: 后端数据模型与API

### Task 4: 创建数据模型

**Files:**
- Create: `assistant/multi-agent-cooperation/backend/app/models/task.py`
- Create: `assistant/multi-agent-cooperation/backend/app/models/team.py`
- Create: `assistant/multi-agent-cooperation/backend/app/models/__init__.py`

- [ ] **Step 1: 创建任务模型**

```python
# assistant/multi-agent-cooperation/backend/app/models/task.py
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
```

- [ ] **Step 2: 创建团队模型**

```python
# assistant/multi-agent-cooperation/backend/app/models/team.py
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
```

- [ ] **Step 3: Commit**

```bash
git add assistant/multi-agent-cooperation/backend/
git commit -m "feat: 创建数据模型"
```

### Task 5: 创建API路由

**Files:**
- Create: `assistant/multi-agent-cooperation/backend/app/api/tasks.py`
- Create: `assistant/multi-agent-cooperation/backend/app/api/templates.py`
- Create: `assistant/multi-agent-cooperation/backend/app/api/__init__.py`

- [ ] **Step 1: 创建任务API**

```python
# assistant/multi-agent-cooperation/backend/app/api/tasks.py
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
```

- [ ] **Step 2: 创建模板API**

```python
# assistant/multi-agent-cooperation/backend/app/api/templates.py
from fastapi import APIRouter, HTTPException
from app.models.team import TeamTemplate
from app.services.template_service import TemplateService
from typing import List

router = APIRouter(prefix="/api/templates", tags=["templates"])
template_service = TemplateService()

@router.get("/", response_model=List[TeamTemplate])
async def list_templates():
    return template_service.list_templates()

@router.get("/{template_id}", response_model=TeamTemplate)
async def get_template(template_id: str):
    template = template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/analyze")
async def analyze_input(user_input: str):
    """分析用户输入，推荐合适的团队模板"""
    return await template_service.analyze_and_recommend(user_input)
```

- [ ] **Step 3: 注册路由到main.py**

```python
# 在 app/main.py 中添加
from app.api import tasks, templates

app.include_router(tasks.router)
app.include_router(templates.router)
```

- [ ] **Step 4: Commit**

```bash
git add assistant/multi-agent-cooperation/backend/
git commit -m "feat: 创建API路由"
```

### Task 6: 创建服务层

**Files:**
- Create: `assistant/multi-agent-cooperation/backend/app/services/task_service.py`
- Create: `assistant/multi-agent-cooperation/backend/app/services/template_service.py`
- Create: `assistant/multi-agent-cooperation/backend/app/services/__init__.py`

- [ ] **Step 1: 创建任务服务**

```python
# assistant/multi-agent-cooperation/backend/app/services/task_service.py
from app.models.task import Task, TaskResponse, TaskStatus
from typing import List, Dict, Any
import asyncio

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
```

- [ ] **Step 2: 创建模板服务**

```python
# assistant/multi-agent-cooperation/backend/app/services/template_service.py
from app.models.team import TeamTemplate
from typing import List, Dict, Any
import json

class TemplateService:
    def __init__(self):
        self.templates = self._load_default_templates()

    def _load_default_templates(self) -> List[TeamTemplate]:
        return [
            TeamTemplate(
                id="dev_team",
                name="软件开发团队",
                description="适用于软件开发项目，包含PM、架构师、前后端开发、测试等角色",
                task_type="dev",
                roles=["ProductManager", "Architect", "FrontendDev", "BackendDev", "QAEngineer"],
                execution_flow=[
                    {"step": 1, "role": "ProductManager", "parallel": False},
                    {"step": 2, "role": "Architect", "parallel": False},
                    {"step": 3, "roles": ["FrontendDev", "BackendDev"], "parallel": True},
                    {"step": 4, "role": "QAEngineer", "parallel": False}
                ]
            ),
            TeamTemplate(
                id="dev_team_lite",
                name="软件开发团队（精简版）",
                description="适用于简单项目，仅包含核心角色",
                task_type="dev",
                roles=["ProductManager", "BackendDev", "QAEngineer"],
                execution_flow=[
                    {"step": 1, "role": "ProductManager"},
                    {"step": 2, "role": "BackendDev"},
                    {"step": 3, "role": "QAEngineer"}
                ]
            ),
            TeamTemplate(
                id="writing_team",
                name="内容创作团队",
                description="适用于内容创作，包含主编、作家、编辑、审稿等角色",
                task_type="writing",
                roles=["ChiefEditor", "Writer", "Editor", "Reviewer"],
                execution_flow=[
                    {"step": 1, "role": "ChiefEditor"},
                    {"step": 2, "role": "Writer"},
                    {"step": 3, "role": "Editor"},
                    {"step": 4, "role": "Reviewer"}
                ]
            )
        ]

    def list_templates(self) -> List[TeamTemplate]:
        return self.templates

    def get_template(self, template_id: str) -> TeamTemplate:
        for t in self.templates:
            if t.id == template_id:
                return t
        return None

    async def analyze_and_recommend(self, user_input: str) -> Dict[str, Any]:
        """分析用户输入，推荐合适的模板"""
        user_input_lower = user_input.lower()

        # 简单的关键词匹配
        dev_keywords = ["开发", "代码", "系统", "网站", "app", "前端", "后端", "软件"]
        writing_keywords = ["文章", "写作", "内容", "文档", "报告", "文案", "创作"]

        is_dev = any(k in user_input_lower for k in dev_keywords)
        is_writing = any(k in user_input_lower for k in writing_keywords)

        if is_dev:
            recommended = "dev_team"
        elif is_writing:
            recommended = "writing_team"
        else:
            recommended = "dev_team"  # 默认

        return {
            "task_type": "dev" if is_dev else "writing",
            "complexity": "normal",
            "recommended_template": recommended,
            "available_templates": [t.id for t in self.templates]
        }
```

- [ ] **Step 3: 测试API**

```bash
cd assistant/multi-agent-cooperation/backend
python run.py &
curl http://localhost:8000/api/templates/
curl http://localhost:8000/api/tasks/
```

- [ ] **Step 4: Commit**

```bash
git add assistant/multi-agent-cooperation/backend/
git commit -m "feat: 创建服务层"
```

---

## Chunk 3: 前端基础页面与API

### Task 7: 创建前端类型定义

**Files:**
- Create: `assistant/multi-agent-cooperation/frontend/src/types/index.ts`

- [ ] **Step 1: 创建TypeScript类型**

```typescript
// assistant/multi-agent-cooperation/frontend/src/types/index.ts

export type TaskStatus =
  | 'pending'
  | 'analyzing'
  | 'team_building'
  | 'executing'
  | 'completed'
  | 'failed'
  | 'paused';

export type TaskType = 'dev' | 'writing';

export type TaskComplexity = 'simple' | 'normal' | 'complex';

export interface Task {
  id: string;
  user_input: string;
  task_type?: TaskType;
  complexity?: TaskComplexity;
  status: TaskStatus;
  template_id?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  progress: number;
  cost: number;
}

export interface TaskCreate {
  user_input: string;
}

export interface TaskResponse {
  id: string;
  status: TaskStatus;
  progress: number;
  message?: string;
}

export interface TeamTemplate {
  id: string;
  name: string;
  description: string;
  task_type: string;
  roles: string[];
  execution_flow: Array<{
    step: number;
    role?: string;
    roles?: string[];
    parallel?: boolean;
  }>;
}

export interface AnalyzeResult {
  task_type: TaskType;
  complexity: TaskComplexity;
  recommended_template: string;
  available_templates: string[];
}

export interface Role {
  name: string;
  status: 'idle' | 'waiting' | 'working' | 'completed' | 'failed';
  output?: any;
}
```

- [ ] **Step 2: Commit**

```bash
git add assistant/multi-agent-cooperation/frontend/src/types/
git commit -m "feat: 添加TypeScript类型定义"
```

### Task 8: 创建前端API客户端

**Files:**
- Create: `assistant/multi-agent-cooperation/frontend/src/api/index.ts`
- Create: `assistant/multi-agent-cooperation/frontend/src/api/tasks.ts`
- Create: `assistant/multi-agent-cooperation/frontend/src/api/templates.ts`

- [ ] **Step 1: 创建Axios配置**

```typescript
// assistant/multi-agent-cooperation/frontend/src/api/index.ts
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;
```

- [ ] **Step 2: 创建任务API**

```typescript
// assistant/multi-agent-cooperation/frontend/src/api/tasks.ts
import api from './index';
import type { Task, TaskCreate, TaskResponse, AnalyzeResult } from '@/types';

export const taskApi = {
  create: (data: TaskCreate) =>
    api.post<TaskResponse>('/tasks/', data),

  list: () =>
    api.get<TaskResponse[]>('/tasks/'),

  get: (id: string) =>
    api.get<TaskResponse>(`/tasks/${id}`),

  start: (id: string) =>
    api.post(`/tasks/${id}/start`),

  pause: (id: string) =>
    api.post(`/tasks/${id}/pause`),

  cancel: (id: string) =>
    api.post(`/tasks/${id}/cancel`)
};
```

- [ ] **Step 3: 创建模板API**

```typescript
// assistant/multi-agent-cooperation/frontend/src/api/templates.ts
import api from './index';
import type { TeamTemplate, AnalyzeResult } from '@/types';

export const templateApi = {
  list: () =>
    api.get<TeamTemplate[]>('/templates/'),

  get: (id: string) =>
    api.get<TeamTemplate>(`/templates/${id}`),

  analyze: (userInput: string) =>
    api.post<AnalyzeResult>('/templates/analyze', userInput, {
      headers: { 'Content-Type': 'text/plain' }
    })
};
```

- [ ] **Step 4: Commit**

```bash
git add assistant/multi-agent-cooperation/frontend/src/api/
git commit -m "feat: 添加前端API客户端"
```

### Task 9: 创建Pinia状态管理

**Files:**
- Create: `assistant/multi-agent-cooperation/frontend/src/stores/task.ts`
- Create: `assistant/multi-agent-cooperation/frontend/src/stores/team.ts`

- [ ] **Step 1: 创建任务Store**

```typescript
// assistant/multi-agent-cooperation/frontend/src/stores/task.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Task, TaskCreate, TaskStatus } from '@/types';
import { taskApi } from '@/api/tasks';

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<Task[]>([]);
  const currentTask = ref<Task | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const pendingTasks = computed(() =>
    tasks.value.filter(t => t.status === 'pending' || t.status === 'paused')
  );

  const activeTasks = computed(() =>
    tasks.value.filter(t => ['analyzing', 'team_building', 'executing'].includes(t.status))
  );

  const completedTasks = computed(() =>
    tasks.value.filter(t => t.status === 'completed' || t.status === 'failed')
  );

  async function createTask(input: string) {
    loading.value = true;
    error.value = null;
    try {
      const response = await taskApi.create({ user_input: input });
      const task: Task = {
        id: response.data.id,
        user_input: input,
        status: response.data.status,
        progress: response.data.progress,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        cost: 0
      };
      tasks.value.unshift(task);
      return task;
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchTasks() {
    loading.value = true;
    try {
      const response = await taskApi.list();
      tasks.value = response.data.map((t: any) => ({
        id: t.id,
        status: t.status,
        progress: t.progress,
        user_input: '',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        cost: 0
      }));
    } finally {
      loading.value = false;
    }
  }

  async function startTask(taskId: string) {
    await taskApi.start(taskId);
    const task = tasks.value.find(t => t.id === taskId);
    if (task) {
      task.status = 'executing';
    }
  }

  return {
    tasks,
    currentTask,
    loading,
    error,
    pendingTasks,
    activeTasks,
    completedTasks,
    createTask,
    fetchTasks,
    startTask
  };
});
```

- [ ] **Step 2: Commit**

```bash
git add assistant/multi-agent-cooperation/frontend/src/stores/
git commit -m "feat: 添加Pinia状态管理"
```

### Task 10: 创建前端页面组件

**Files:**
- Create: `assistant/multi-agent-cooperation/frontend/src/views/HomeView.vue`
- Create: `assistant/multi-agent-cooperation/frontend/src/views/TaskView.vue`
- Create: `assistant/multi-agent-cooperation/frontend/src/router/index.ts`

- [ ] **Step 1: 创建路由配置**

```typescript
// assistant/multi-agent-cooperation/frontend/src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/HomeView.vue';
import TaskView from '@/views/TaskView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/task/:id',
      name: 'task',
      component: TaskView
    }
  ]
});

export default router;
```

- [ ] **Step 2: 创建首页**

```vue
<!-- assistant/multi-agent-cooperation/frontend/src/views/HomeView.vue -->
<template>
  <div class="home">
    <div class="container">
      <h1>多Agent协作系统</h1>
      <p class="subtitle">输入您的需求，AI团队将为您完成</p>

      <el-card class="input-card">
        <el-input
          v-model="userInput"
          type="textarea"
          :rows="6"
          placeholder="例如：帮我开发一个用户管理系统，需要用户登录、文章发布、评论功能"
        />

        <div class="actions">
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleAnalyze"
          >
            分析需求
          </el-button>
        </div>
      </el-card>

      <!-- 模板选择 -->
      <el-card v-if="showTemplateSelect" class="template-card">
        <template #header>
          <span>选择团队模板</span>
        </template>

        <div class="analysis-result">
          <el-tag>任务类型: {{ analysisResult?.task_type }}</el-tag>
          <el-tag type="warning">复杂度: {{ analysisResult?.complexity }}</el-tag>
        </div>

        <el-radio-group v-model="selectedTemplate">
          <el-radio
            v-for="template in templates"
            :key="template.id"
            :value="template.id"
            border
          >
            <div class="template-option">
              <div class="template-name">{{ template.name }}</div>
              <div class="template-desc">{{ template.description }}</div>
              <div class="template-roles">
                角色: {{ template.roles.join(', ') }}
              </div>
            </div>
          </el-radio>
        </el-radio-group>

        <div class="actions">
          <el-button @click="showTemplateSelect = false">上一步</el-button>
          <el-button type="primary" @click="handleCreateTask">确认并执行</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useTaskStore } from '@/stores/task';
import { templateApi } from '@/api/templates';
import type { TeamTemplate, AnalyzeResult } from '@/types';
import { ElMessage } from 'element-plus';

const router = useRouter();
const taskStore = useTaskStore();

const userInput = ref('');
const loading = ref(false);
const showTemplateSelect = ref(false);
const analysisResult = ref<AnalyzeResult | null>(null);
const selectedTemplate = ref('');
const templates = ref<TeamTemplate[]>([]);

async function handleAnalyze() {
  if (!userInput.value.trim()) {
    ElMessage.warning('请输入需求描述');
    return;
  }

  loading.value = true;
  try {
    const [templatesRes, analyzeRes] = await Promise.all([
      templateApi.list(),
      templateApi.analyze(userInput.value)
    ]);

    templates.value = templatesRes.data;
    analysisResult.value = analyzeRes.data;
    selectedTemplate.value = analyzeRes.data.recommended_template;
    showTemplateSelect.value = true;
  } catch (e) {
    ElMessage.error('分析失败，请重试');
  } finally {
    loading.value = false;
  }
}

async function handleCreateTask() {
  if (!selectedTemplate.value) {
    ElMessage.warning('请选择团队模板');
    return;
  }

  loading.value = true;
  try {
    const task = await taskStore.createTask(userInput.value);
    ElMessage.success('任务创建成功');
    router.push(`/task/${task.id}`);
  } catch (e) {
    ElMessage.error('创建失败');
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  padding: 40px 20px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: #303133;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  color: #909399;
  margin-bottom: 32px;
}

.input-card,
.template-card {
  margin-top: 24px;
}

.actions {
  margin-top: 20px;
  text-align: center;
}

.analysis-result {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.template-option {
  padding: 8px 0;
}

.template-name {
  font-weight: bold;
  margin-bottom: 4px;
}

.template-desc {
  font-size: 12px;
  color: #909399;
}

.template-roles {
  font-size: 12px;
  color: #67c23a;
  margin-top: 4px;
}

.el-radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
```

- [ ] **Step 3: 创建任务详情页**

```vue
<!-- assistant/multi-agent-cooperation/frontend/src/views/TaskView.vue -->
<template>
  <div class="task-view">
    <div class="container">
      <el-page-header @back="goHome" title="返回首页">
        <template #content>
          <span class="task-title">任务详情</span>
        </template>
      </el-page-header>

      <el-card class="task-card">
        <template #header>
          <div class="card-header">
            <span>任务进度</span>
            <el-tag :type="statusType">{{ task?.status || 'pending' }}</el-tag>
          </div>
        </template>

        <el-progress
          :percentage="task?.progress || 0"
          :status="progressStatus"
          :stroke-width="20"
        />

        <div class="task-info">
          <div class="info-item">
            <span class="label">任务描述：</span>
            <span>{{ task?.user_input }}</span>
          </div>
          <div class="info-item">
            <span class="label">创建时间：</span>
            <span>{{ formatTime(task?.created_at) }}</span>
          </div>
        </div>

        <div class="actions">
          <el-button
            v-if="task?.status === 'pending' || task?.status === 'paused'"
            type="primary"
            @click="handleStart"
          >
            开始执行
          </el-button>
          <el-button
            v-if="task?.status === 'executing'"
            @click="handlePause"
          >
            暂停
          </el-button>
          <el-button
            v-if="task?.status !== 'completed' && task?.status !== 'failed'"
            type="danger"
            @click="handleCancel"
          >
            取消
          </el-button>
        </div>
      </el-card>

      <!-- Agent状态 -->
      <el-card class="agents-card">
        <template #header>
          <span>Agent状态</span>
        </template>

        <div class="agents-grid">
          <div v-for="role in roles" :key="role.name" class="agent-item">
            <el-tag :type="getRoleStatusType(role.status)">
              {{ role.status }}
            </el-tag>
            <span class="role-name">{{ role.name }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { taskApi } from '@/api/tasks';
import type { Task, Role } from '@/types';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();

const taskId = computed(() => route.params.id as string);
const task = ref<Task | null>(null);
const roles = ref<Role[]>([
  { name: 'ProductManager', status: 'idle' },
  { name: 'Architect', status: 'idle' },
  { name: 'FrontendDev', status: 'idle' },
  { name: 'BackendDev', status: 'idle' },
  { name: 'QAEngineer', status: 'idle' }
]);

const statusType = computed(() => {
  const map: Record<string, string> = {
    pending: 'info',
    analyzing: 'warning',
    team_building: 'warning',
    executing: 'primary',
    completed: 'success',
    failed: 'danger',
    paused: 'warning'
  };
  return map[task.value?.status || 'pending'] || 'info';
});

const progressStatus = computed(() => {
  if (task.value?.status === 'completed') return 'success';
  if (task.value?.status === 'failed') return 'exception';
  return undefined;
});

function formatTime(time?: string) {
  if (!time) return '-';
  return new Date(time).toLocaleString();
}

function getRoleStatusType(status: string) {
  const map: Record<string, string> = {
    idle: 'info',
    waiting: 'warning',
    working: 'primary',
    completed: 'success',
    failed: 'danger'
  };
  return map[status] || 'info';
}

function goHome() {
  router.push('/');
}

async function handleStart() {
  await taskApi.start(taskId.value);
  ElMessage.success('任务已开始');
}

async function handlePause() {
  await taskApi.pause(taskId.value);
  ElMessage.info('任务已暂停');
}

async function handleCancel() {
  await taskApi.cancel(taskId.value);
  ElMessage.warning('任务已取消');
}

onMounted(async () => {
  try {
    const response = await taskApi.get(taskId.value);
    task.value = {
      id: response.data.id,
      status: response.data.status,
      progress: response.data.progress,
      user_input: '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      cost: 0
    };
  } catch (e) {
    ElMessage.error('获取任务失败');
  }
});
</script>

<style scoped>
.task-view {
  min-height: 100vh;
  padding: 24px;
}

.container {
  max-width: 900px;
  margin: 0 auto;
}

.task-title {
  font-size: 18px;
  font-weight: bold;
}

.task-card,
.agents-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-info {
  margin-top: 20px;
}

.info-item {
  margin-bottom: 12px;
  display: flex;
  gap: 8px;
}

.label {
  color: #909399;
  flex-shrink: 0;
}

.actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.agent-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.role-name {
  font-weight: 500;
}
</style>
```

- [ ] **Step 4: 测试前端**

```bash
cd assistant/multi-agent-cooperation/frontend
npm run dev
# 访问 http://localhost:3000
```

- [ ] **Step 5: Commit**

```bash
git add assistant/multi-agent-cooperation/frontend/
git commit -m "feat: 添加前端页面"
```

---

## Chunk 4: Agent核心模块（后端）

### Task 11: 创建TeamManager核心模块

**Files:**
- Create: `assistant/multi-agent-cooperation/backend/app/agents/team_manager.py`
- Create: `assistant/multi-agent-cooperation/backend/app/agents/__init__.py`

- [ ] **Step 1: 创建TeamManager**

```python
# assistant/multi-agent-cooperation/backend/app/agents/team_manager.py
from typing import Dict, Any, List, Optional
from app.models.task import Task, TaskStatus, TaskType, TaskComplexity
from app.models.team import Team, TeamTemplate, Role
from app.agents.team_leader import TeamLeader
from app.agents.agent_factory import AgentFactory
from app.config import settings
import uuid

class TaskAnalyzer:
    """任务分析器"""

    def analyze(self, user_input: str) -> Dict[str, Any]:
        """分析用户输入，返回任务类型和复杂度"""
        input_lower = user_input.lower()

        # 关键词匹配
        dev_keywords = ["开发", "代码", "系统", "网站", "app", "前端", "后端", "软件", "接口"]
        writing_keywords = ["文章", "写作", "内容", "文档", "报告", "文案", "创作", "写一篇"]

        # 复杂度判断
        complexity = TaskComplexity.NORMAL
        if len(user_input) < 20:
            complexity = TaskComplexity.SIMPLE
        elif len(user_input) > 200:
            complexity = TaskComplexity.COMPLEX

        is_dev = any(k in input_lower for k in dev_keywords)
        task_type = TaskType.DEV if is_dev else TaskType.WRITING

        return {
            "task_type": task_type,
            "complexity": complexity,
            "keywords": []
        }

class TeamManager:
    """
    TeamManager - 顶层协调者
    职责：任务理解、团队组建、进度协调、结果验收
    """

    def __init__(self):
        self.analyzer = TaskAnalyzer()
        self.agent_factory = AgentFactory()
        self.active_teams: Dict[str, Team] = {}

    def analyze_task(self, user_input: str) -> Dict[str, Any]:
        """分析任务，返回任务类型和复杂度"""
        return self.analyzer.analyze(user_input)

    def build_team(self, template_id: str, task_id: str) -> Team:
        """根据模板组建团队"""
        template = self.agent_factory.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # 创建角色
        roles = []
        for role_name in template.roles:
            role = Role(name=role_name, status="idle", dependencies=[])
            roles.append(role)

        team = Team(
            task_id=task_id,
            template_id=template_id,
            roles=roles,
            status="ready"
        )

        self.active_teams[task_id] = team
        return team

    async def coordinate(self, task_id: str) -> Dict[str, Any]:
        """协调团队执行任务"""
        team = self.active_teams.get(task_id)
        if not team:
            return {"error": "Team not found"}

        # 创建TeamLeader并执行
        template = self.agent_factory.get_template(team.template_id)
        team_leader = TeamLeader(
            team=team,
            template=template,
            agent_factory=self.agent_factory
        )

        result = await team_leader.execute()
        return result

    def get_team_status(self, task_id: str) -> Optional[Team]:
        """获取团队状态"""
        return self.active_teams.get(task_id)

# 全局实例
team_manager = TeamManager()
```

- [ ] **Step 2: Commit**

```bash
git add assistant/multi-agent-cooperation/backend/app/agents/
git commit -m "feat: 添加TeamManager核心模块"
```

### Task 12: 创建TeamLeader模块

**Files:**
- Create: `assistant/multi-agent-cooperation/backend/app/agents/team_leader.py`

- [ ] **Step 1: 创建TeamLeader**

```python
# assistant/multi-agent-cooperation/backend/app/agents/team_leader.py
from typing import Dict, Any, List
from app.models.team import Team, TeamTemplate, Role
from app.agents.agent_factory import AgentFactory

class TeamLeader:
    """
    TeamLeader - 领域协调者
    职责：子任务分解、分配给执行Agent、结果汇总
    """

    def __init__(self, team: Team, template: TeamTemplate, agent_factory: AgentFactory):
        self.team = team
        self.template = template
        self.agent_factory = agent_factory

    async def execute(self) -> Dict[str, Any]:
        """执行团队任务"""
        results = {}

        for flow_step in self.template.execution_flow:
            step = flow_step["step"]

            # 判断是否并行执行
            if flow_step.get("parallel", False):
                roles_to_execute = flow_step.get("roles", [])
                # 并行执行
                step_results = await self._execute_parallel(roles_to_execute)
            else:
                role_name = flow_step.get("role")
                if role_name:
                    step_results = await self._execute_role(role_name)

            results[f"step_{step}"] = step_results

        return {
            "status": "completed",
            "results": results
        }

    async def _execute_role(self, role_name: str) -> Dict[str, Any]:
        """执行单个角色任务"""
        # 找到对应角色
        role = None
        for r in self.team.roles:
            if r.name == role_name:
                role = r
                break

        if not role:
            return {"error": f"Role {role_name} not found"}

        # 更新状态
        role.status = "working"

        try:
            # 获取Agent并执行
            agent = self.agent_factory.create_agent(role_name)
            result = await agent.run(f"执行{role_name}任务")

            role.status = "completed"
            role.output = result

            return {
                "role": role_name,
                "status": "completed",
                "output": result
            }
        except Exception as e:
            role.status = "failed"
            return {
                "role": role_name,
                "status": "failed",
                "error": str(e)
            }

    async def _execute_parallel(self, role_names: List[str]) -> Dict[str, Any]:
        """并行执行多个角色"""
        import asyncio

        tasks = [self._execute_role(name) for name in role_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "roles": role_names,
            "results": results
        }
```

- [ ] **Step 2: Commit**

```bash
git add assistant/multi-agent-cooperation/backend/app/agents/
git commit -m "feat: 添加TeamLeader模块"
```

### Task 13: 创建AgentFactory模块

**Files:**
- Create: `assistant/multi-agent-cooperation/backend/app/agents/agent_factory.py`
- Create: `assistant/multi-agent-cooperation/backend/app/agents/templates/dev_team.py`
- Create: `assistant/multi-agent-cooperation/backend/app/agents/templates/writing_team.py`

- [ ] **Step 1: 创建AgentFactory**

```python
# assistant/multi-agent-cooperation/backend/app/agents/agent_factory.py
from typing import Dict, Any, Optional
from app.models.team import TeamTemplate
from app.agents.templates.dev_team import DEV_TEAM_TEMPLATE
from app.agents.templates.writing_team import WRITING_TEAM_TEMPLATE

# 简单的Agent实例池
class AgentPool:
    """Agent实例池"""

    def __init__(self, max_size: int = 5):
        self.max_size = max_size
        self.pools: Dict[str, list] = {}  # role_name -> [agents]

    def get(self, role_name: str):
        """获取Agent实例"""
        if role_name not in self.pools:
            self.pools[role_name] = []

        pool = self.pools[role_name]
        if pool:
            return pool.pop()

        return None

    def release(self, role_name: str, agent):
        """释放Agent实例回池"""
        if role_name not in self.pools:
            self.pools[role_name] = []

        pool = self.pools[role_name]
        if len(pool) < self.max_size:
            pool.append(agent)

class SimpleAgent:
    """简单的Agent实现（基于LLM）"""

    def __init__(self, role_name: str, role_prompt: str):
        self.role_name = role_name
        self.role_prompt = role_prompt

    async def run(self, task: str) -> str:
        """执行任务"""
        # 这里应该调用真实的LLM
        # 目前返回模拟结果
        return f"[{self.role_name}] 已完成: {task}"

class AgentFactory:
    """
    AgentFactory - Agent工厂
    职责：角色模板管理、Agent实例创建
    """

    def __init__(self):
        self.templates: Dict[str, TeamTemplate] = {
            "dev_team": DEV_TEAM_TEMPLATE,
            "dev_team_lite": DEV_TEAM_TEMPLATE,
            "writing_team": WRITING_TEAM_TEMPLATE
        }
        self.role_prompts = self._load_role_prompts()
        self.agent_pool = AgentPool()

    def _load_role_prompts(self) -> Dict[str, str]:
        """加载角色Prompt"""
        return {
            "ProductManager": "你是一名资深产品经理，擅长需求分析和PRD撰写。",
            "Architect": "你是一名系统架构师，擅长技术方案设计。",
            "FrontendDev": "你是一名前端开发工程师，擅长Vue/React开发。",
            "BackendDev": "你是一名后端开发工程师，擅长Python/Go开发。",
            "QAEngineer": "你是一名QA工程师，擅长测试用例编写。",
            "ChiefEditor": "你是一名主编，擅长内容策划和整体把控。",
            "Writer": "你是一名专业作家，擅长各类文章撰写。",
            "Editor": "你是一名文字编辑，擅长润色和优化。",
            "Reviewer": "你是一名审稿专家，擅长内容审核和质量评估。"
        }

    def get_template(self, template_id: str) -> Optional[TeamTemplate]:
        """获取团队模板"""
        return self.templates.get(template_id)

    def list_templates(self):
        """列出所有模板"""
        return list(self.templates.values())

    def create_agent(self, role_name: str):
        """创建Agent实例"""
        # 尝试从池中获取
        agent = self.agent_pool.get(role_name)
        if agent:
            return agent

        # 创建新实例
        role_prompt = self.role_prompts.get(role_name, f"你是一个{role_name}。")
        return SimpleAgent(role_name, role_prompt)

    def release_agent(self, role_name: str, agent):
        """释放Agent实例"""
        self.agent_pool.release(role_name, agent)
```

- [ ] **Step 2: 创建团队模板**

```python
# assistant/multi-agent-cooperation/backend/app/agents/templates/dev_team.py
from app.models.team import TeamTemplate

DEV_TEAM_TEMPLATE = TeamTemplate(
    id="dev_team",
    name="软件开发团队",
    description="适用于软件开发项目",
    task_type="dev",
    roles=[
        "ProductManager",
        "Architect",
        "FrontendDev",
        "BackendDev",
        "QAEngineer"
    ],
    execution_flow=[
        {"step": 1, "role": "ProductManager", "parallel": False},
        {"step": 2, "role": "Architect", "parallel": False},
        {"step": 3, "roles": ["FrontendDev", "BackendDev"], "parallel": True},
        {"step": 4, "role": "QAEngineer", "parallel": False}
    ]
)
```

```python
# assistant/multi-agent-cooperation/backend/app/agents/templates/writing_team.py
from app.models.team import TeamTemplate

WRITING_TEAM_TEMPLATE = TeamTemplate(
    id="writing_team",
    name="内容创作团队",
    description="适用于内容创作",
    task_type="writing",
    roles=[
        "ChiefEditor",
        "Writer",
        "Editor",
        "Reviewer"
    ],
    execution_flow=[
        {"step": 1, "role": "ChiefEditor", "parallel": False},
        {"step": 2, "role": "Writer", "parallel": False},
        {"step": 3, "role": "Editor", "parallel": False},
        {"step": 4, "role": "Reviewer", "parallel": False}
    ]
)
```

- [ ] **Step 3: Commit**

```bash
git add assistant/multi-agent-cooperation/backend/app/agents/
git commit -m "feat: 添加AgentFactory和团队模板"
```

---

## 执行说明

**Plan complete and saved to `docs/superpowers/plans/2026-03-19-multi-agent-cooperation-plan.md`. Ready to execute?**

由于这是一个复杂的前后端分离项目，建议分块执行：

1. **Chunk 1**: 项目初始化 - 创建后端和前端基础结构
2. **Chunk 2**: 后端数据模型与API
3. **Chunk 3**: 前端基础页面与API
4. **Chunk 4**: Agent核心模块

每个Chunk可以独立测试和验证。建议使用subagent-driven-development来并行执行各个任务块。
