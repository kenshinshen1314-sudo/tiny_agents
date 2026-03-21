# 多Agent协作平台设计文档

## 1. 项目概述

### 1.1 项目名称
**Multi-Agent Team Platform** - 多Agent协作应用平台

### 1.2 项目目标
构建一个基于tiny_agents框架的多Agent协作应用平台，支持通过预定义模板快速组建Agent团队，完成软件开发、内容创作等任务。

### 1.3 核心价值
- 用户输入需求或PRD文档，自动组建合适的Agent团队
- 支持软件开发、内容创作两大场景
- 团队模板可编辑，灵活配置
- 协调者统一调度，清晰可控

---

## 2. 需求分析

### 2.1 功能需求

| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| F01 | 用户输入需求（文本+附件） | P0 |
| F02 | 选择团队模板 | P0 |
| F03 | 编辑团队模板（增删角色、调整配置） | P0 |
| F04 | 执行任务并返回结果 | P0 |
| F05 | 保存中间过程和协作记录 | P1 |
| F06 | 模板管理（创建、编辑、删除、复制） | P1 |
| F07 | 任务历史记录 | P1 |
| F08 | 任务执行状态实时展示（SSE进度推送） | P1 |
| F09 | 用户对输出质量进行评分和反馈 | P2 |
| F10 | 模板配置校验（协调者、prompt、工具） | P1 |
| F11 | LLM模型全局配置管理 | P2 |
| F12 | 附件类型识别与预处理 | P2 |

### 2.2 非功能需求

| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| NF01 | 界面简洁易用 | P0 |
| NF02 | 响应及时（单次Agent调用<30s） | P1 |
| NF03 | 数据持久化 | P0 |
| NF04 | 执行进度可追溯 | P1 |
| NF05 | 输出质量可评估 | P2 |

---

## 3. 技术架构

### 3.1 技术栈

**前端**：
- TypeScript
- Vue 3（Composition API）
- Vite
- Axios

**后端**：
- Python
- FastAPI
- tiny_agents（核心框架）
- SQLite（关系型存储）

### 3.2 架构模式

**中央调度模式**：
```
用户 → 前端 → FastAPI（协调者） → Agent执行 → 返回结果
                     ↓
              共享上下文存储
```

- 协调者作为唯一API入口
- Agent执行结果写入共享上下文
- 简洁实现，易于维护和调试

---

## 4. 数据模型

### 4.1 核心实体

#### TeamTemplate（团队模板）
```python
{
    "id": "uuid",
    "name": "str",           # 模板名称
    "description": "str",    # 模板描述
    "category": "str",       # 类别：development/content
    "roles": [                # 角色列表
        {
            "id": "uuid",
            "name": "str",           # 角色名称
            "description": "str",    # 职责描述
            "system_prompt": "str", # System Prompt
            "tools": ["str"],        # 可用工具列表
            "model": "str",          # LLM模型
            "temperature": "float", # 温度参数
            "is_coordinator": "bool" # 是否为协调者
        }
    ],
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### Task（任务）
```python
{
    "id": "uuid",
    "name": "str",           # 任务名称
    "user_input": "str",     # 用户输入需求
    "attachments": ["str"],  # 附件路径列表
    "template_id": "uuid",   # 使用的模板ID
    "status": "str",         # pending/running/completed/failed
    "current_step": "str",  # 当前执行步骤（如"FrontendDev开发中"）
    "progress": "int",       # 进度百分比 0-100
    "result": "str",         # 最终结果
    "context": "dict",      # 共享上下文
    "history": [             # 协作记录
        {
            "role": "str",
            "input": "str",
            "output": "str",
            "timestamp": "datetime"
        }
    ],
    "feedback": {            # 用户反馈
        "rating": "int",     # 评分 1-5
        "comment": "str",    # 反馈内容
        "created_at": "datetime"
    },
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### LLMConfig（LLM模型配置）
```python
{
    "id": "uuid",
    "name": "str",           # 配置名称
    "provider": "str",       # 提供商：openai/deepseek/qwen/kimi/zhipu
    "model": "str",          # 模型名称
    "api_key": "str",        # API Key（可加密存储）
    "base_url": "str",       # 自定义API地址
    "temperature": "float",  # 默认温度
    "max_tokens": "int",     # 最大token数
    "is_default": "bool",   # 是否为默认配置
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### 4.2 预置模板

#### 软件开发团队模板
- **Coordinator**：需求分析、任务分解、结果汇总
- **ProductManager**：PRD编写、需求细化
- **Architect**：技术方案设计
- **FrontendDev**：前端开发
- **BackendDev**：后端开发
- **QA**：测试用例编写

#### 内容创作团队模板
- **Coordinator**：任务分解、内容统筹
- **Writer**：初稿撰写
- **Editor**：内容编辑、润色
- **Reviewer**：审稿、反馈

---

## 5. 核心流程

### 5.1 任务执行流程

```
1. 用户输入需求（文本+附件）
   ↓
2. 选择团队模板
   ↓
3. 查看/编辑角色配置（如需要）
   ↓
4. 确认执行
   ↓
5. 协调者Agent接收需求，分析并分解任务
   ↓
6. 协调者按需调用各Agent执行子任务
   ↓
7. 每个Agent的结果写入共享上下文
   ↓
8. 协调者汇总所有结果
   ↓
9. 返回最终结果 + 中间过程记录
```

### 5.2 模板管理流程

```
1. 选择预置模板或新建模板
   ↓
2. 编辑模板信息（名称、描述）
   ↓
3. 添加/编辑/删除角色
   ↓
4. 配置每个角色的prompt、工具、模型
   ↓
5. 保存模板
```

---

## 5.3 执行状态实时展示

采用SSE（Server-Sent Events）实现实时进度推送：

```
前端 ←SSE← FastAPI ← Agent执行
```

**推送事件类型**：
| 事件 | 说明 |
|------|------|
| task_started | 任务开始 |
| step_start | 某个Agent开始执行 |
| step_complete | 某个Agent完成 |
| step_error | 某个Agent执行出错 |
| task_complete | 任务完成 |
| task_error | 任务执行失败 |

**实现方案**：
- 前端使用 EventSource 监听 `/api/tasks/{id}/stream`
- 每个step更新时推送当前进度和状态
- 前端实时更新UI展示当前执行到哪个角色

---

## 5.4 质量评估机制

用户可对输出结果进行评分和反馈：

**评分维度**：
| 维度 | 说明 |
|------|------|
| 整体满意度 | 1-5分 |
| 结果准确性 | 1-5分 |
| 响应速度 | 1-5分（可选） |

**反馈内容**：
- 文字评价
- 标记具体问题（可选择问题类型）

**数据应用**：
- 收集反馈数据用于优化Agent prompt
- 高频问题可作为模板迭代参考

---

## 5.5 模板校验逻辑

模板保存时进行以下校验：

| 校验项 | 规则 | 错误提示 |
|--------|------|----------|
| 协调者存在 | 必须有且仅有一个 `is_coordinator=true` 的角色 | "模板必须包含一个协调者角色" |
| 角色名称非空 | 每个角色必须有名称 | "角色名称不能为空" |
| System Prompt非空 | 每个角色必须有prompt | "角色的System Prompt不能为空" |
| 工具有效性 | 工具必须在系统中存在 | "工具[{name}]不存在" |
| 模板名称唯一 | 同类别下名称不能重复 | "模板名称已存在" |

---

## 5.6 LLM模型配置管理

**功能**：
- 支持配置多个LLM模型（OpenAI、DeepSeek、Qwen、Kimi、智谱等）
- 角色可选择使用哪个模型配置
- 支持设置默认模型

**配置项**：
- 提供商（provider）
- 模型名称（model）
- API Key
- 自定义API地址（base_url）
- 温度参数（temperature）
- 最大token数（max_tokens）

**角色中的模型引用**：
- 角色可指定使用哪个LLMConfig
- 未指定时使用系统默认配置

---

## 5.7 附件类型处理

**支持的文件格式**：
| 类型 | 格式 | 处理策略 |
|------|------|----------|
| 文本 | .txt, .md | 直接读取内容 |
| PDF | .pdf | 提取文本（使用PyPDF2） |
| Word | .docx | 提取文本（使用python-docx） |
| 代码 | .py, .js, .ts, .json 等 | 读取内容并识别语言 |

**处理流程**：
```
1. 用户上传附件
   ↓
2. 识别文件类型
   ↓
3. 调用对应的解析器提取文本
   ↓
4. 将文本内容加入用户输入上下文
   ↓
5. 传递给Agent处理
```

**限制**：
- 单个文件大小限制：10MB
- 总附件大小限制：50MB
- 不支持的类型返回错误提示

---

## 6. API设计

### 6.1 模板管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/templates | 获取模板列表 |
| GET | /api/templates/{id} | 获取模板详情 |
| POST | /api/templates | 创建模板 |
| PUT | /api/templates/{id} | 更新模板 |
| DELETE | /api/templates/{id} | 删除模板 |

### 6.2 任务管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/tasks | 获取任务列表 |
| GET | /api/tasks/{id} | 获取任务详情 |
| POST | /api/tasks | 创建任务并执行 |
| GET | /api/tasks/{id}/history | 获取协作记录 |

### 6.3 文件上传

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/upload | 上传附件 |

### 6.4 任务执行状态（SSE）

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/tasks/{id}/stream | SSE实时进度推送 |

### 6.5 质量反馈

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/tasks/{id}/feedback | 提交质量评分和反馈 |

### 6.6 LLM配置管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/llm-configs | 获取LLM配置列表 |
| GET | /api/llm-configs/{id} | 获取配置详情 |
| POST | /api/llm-configs | 创建LLM配置 |
| PUT | /api/llm-configs/{id} | 更新LLM配置 |
| DELETE | /api/llm-configs/{id} | 删除LLM配置 |

### 6.7 模板校验

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/templates/validate | 校验模板配置 |

---

## 7. 前端设计

### 7.1 页面结构

1. **首页**：模板选择、新建任务
2. **任务执行页**：输入需求、选择模板、编辑配置、执行、查看结果
3. **模板管理页**：模板列表、新建/编辑模板
4. **历史记录页**：历史任务列表、详情查看

### 7.2 核心组件

- TemplateCard：模板卡片展示
- RoleEditor：角色配置编辑器
- TaskRunner：任务执行器
- ResultViewer：结果展示器
- HistoryViewer：历史记录查看器
- ProgressBar：实时进度条（SSE推送）
- FeedbackPanel：质量评分反馈面板
- LLMConfigPanel：LLM模型配置面板

### 7.3 前端状态管理

使用Vue Reactive：

```
- taskStore：任务状态（执行中/已完成/失败）
- currentStep：当前执行步骤
- progress：进度百分比
- templates：模板列表
- llmConfigs：LLM配置列表
```

---

## 8. 实施计划

### Phase 1：基础功能
- 后端API基础搭建
- SQLite数据模型
- 预置模板定义
- 前端基础框架

### Phase 2：核心流程
- 任务创建和执行
- Agent协调调度
- 结果返回
- SSE实时进度推送

### Phase 3：完善功能
- 模板编辑功能（含校验逻辑）
- 历史记录
- 中间过程展示
- LLM配置管理
- 质量反馈机制
- 附件上传处理

---

## 9. 风险与限制

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Agent执行时间过长 | 用户体验差 | 设置超时、逐步返回 |
| Agent输出质量不稳定 | 结果不可用 | 允许用户重试、手动调整 |
| 并发能力有限 | 多任务处理慢 | 后续升级任务队列 |

---

## 10. 后续扩展

- 支持消息队列（Celery）实现并行执行
- 添加向量数据库支持语义搜索
- 引入MCP/A2A协议实现分布式Agent
- Docker容器化部署
