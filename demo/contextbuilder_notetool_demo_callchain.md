# ContextBuilder + NoteTool Demo 调用链分析

> 文件位置: `tiny_agents/demo/contextbuilder_notetool_demo.py`
> 生成时间: 2026-03-11

## 概述

`contextbuilder_notetool_demo.py` 演示了如何将 `ContextBuilder` 和 `NoteTool` 集成到一个长期项目助手 `ProjectAssistant` 中。该助手结合了：

- **ContextBuilder**: GSSC 上下文构建流水线
- **NoteTool**: 结构化笔记管理
- **MemoryTool**: 工作记忆存储
- **RAGTool**: 知识库检索

---

## 主函数执行流程

```python
if __name__ == "__main__":
    # 1. 创建助手实例
    assistant = ProjectAssistant(
        name="项目助手",
        project_name="data_pipeline_refactoring"
    )

    # 2. 第一次交互（记录项目状态，自动保存笔记）
    response = assistant.run(
        "我们已经完成了数据模型层的重构,测试覆盖率达到85%。下一步计划重构业务逻辑层。",
        note_as_action=True
    )

    # 3. 第二次交互（提出问题）
    response = assistant.run(
        "在重构业务逻辑层时,我遇到了依赖版本冲突的问题,该如何解决?"
    )

    # 4. 查看笔记摘要
    summary = assistant.note_tool.run({"action": "summary"})
    print(summary)
```

---

## 阶段一：初始化 (`ProjectAssistant.__init__`)

### 调用链图

```
ProjectAssistant.__init__(name, project_name)
│
├─→ SimpleAgent.__init__(name, llm=HelloAgentsLLM())
│   └─→ Agent.__init__(name, llm, system_prompt=None, config=None)
│       └─→ 初始化基础 Agent 属性
│           ├─→ self.name = name
│           ├─→ self.llm = llm
│           ├─→ self.system_prompt = system_prompt
│           └─→ self._history = []
│
├─→ self.project_name = project_name
│
├─→ MemoryTool(user_id=project_name)
│   └─→ tiny_agents/tools/builtin/memory_tool.py
│       ├─→ Tool.__init__(name="memory", description=...)
│       ├─→ self.user_id = user_id
│       ├─→ self.storage = WorkingMemoryStorage()
│       └─→ 初始化工作记忆存储
│
├─→ RAGTool(knowledge_base_path=f"./{project_name}_kb")
│   └─→ tiny_agents/tools/builtin/rag_tool.py
│       ├─→ Tool.__init__(name="rag", description=...)
│       ├─→ self.kb_path = Path(knowledge_base_path)
│       ├─→ self.index = None
│       └─→ 初始化 RAG 知识库
│
├─→ NoteTool(workspace=f"./{project_name}_notes")
│   └─→ tiny_agents/tools/builtin/note_tool.py
│       ├─→ Tool.__init__(name="note", description=...)
│       ├─→ self.workspace = Path(workspace)
│       ├─→ self.workspace.mkdir(parents=True, exist_ok=True)
│       ├─→ self.index_file = workspace / "notes_index.json"
│       ├─→ _load_index()
│       │   ├─→ 读取 notes_index.json
│       │   └─→ 初始化或加载笔记索引
│       │       └─→ {"notes": [], "metadata": {...}}
│       └─→ 初始化笔记工作区
│
├─→ ContextBuilder(
│       memory_tool=self.memory_tool,
│       rag_tool=self.rag_tool,
│       config=ContextConfig(max_tokens=4000)
│   )
│   └─→ tiny_agents/context/builder.py
│       ├─→ self.memory_tool = memory_tool
│       ├─→ self.rag_tool = rag_tool
│       ├─→ self.config = config or ContextConfig()
│       └─→ self._encoding = tiktoken.get_encoding("cl100k_base")
│
└─→ self.conversation_history = []
```

### 详细说明

| 组件 | 文件路径 | 说明 |
|-----|---------|------|
| `SimpleAgent` | `tiny_agents/agents/simple_agent.py` | 基础对话 Agent |
| `MemoryTool` | `tiny_agents/tools/builtin/memory_tool.py` | 工作记忆存储 |
| `RAGTool` | `tiny_agents/tools/builtin/rag_tool.py` | 知识库检索 |
| `NoteTool` | `tiny_agents/tools/builtin/note_tool.py` | 结构化笔记管理 |
| `ContextBuilder` | `tiny_agents/context/builder.py` | GSSC 上下文构建 |

---

## 阶段二：第一次交互 (`run()` with `note_as_action=True`)

### 调用链图

```
assistant.run(
    "我们已经完成了数据模型层的重构,测试覆盖率达到85%。下一步计划重构业务逻辑层。",
    note_as_action=True
)
│
├─→ 【步骤1】_retrieve_relevant_notes(user_input)
│   │
│   ├─→ note_tool.run({
│   │       "action": "list",
│   │       "note_type": "blocker",
│   │       "limit": 2
│   │   })
│   │   └─→ NoteTool.run() → _list_notes()
│   │       ├─→ 从 notes_index["notes"] 过滤
│   │       ├─→ filtered_notes = [n for n in notes if n["type"] == "blocker"]
│   │       ├─→ 限制返回数量
│   │       └─→ 返回: "📝 笔记列表...\n• [blocker] 标题\n..."
│   │
│   ├─→ note_tool.run({
│   │       "action": "search",
│   │       "query": query,
│   │       "limit": limit
│   │   })
│   │   └─→ NoteTool.run() → _search_notes()
│   │       ├─→ 遍历 notes_index["notes"]
│   │       ├─→ 对每个笔记:
│   │       │   ├─→ _get_note_path(note_id) → 获取 .md 文件路径
│   │       │   ├─→ 读取 Markdown 文件
│   │       │   ├─→ _markdown_to_note() → 解析 YAML frontmatter
│   │       │   └─→ 检查标题/内容/标签是否匹配 query
│   │       ├─→ 限制返回数量
│   │       └─→ 返回: "🔍 搜索结果...\n[note_id] 标题..."
│   │
│   ├─→ 合并去重: {note['note_id']: note for note in blockers + search_results}
│   └─→ 返回: List[Dict] 笔记列表
│
├─→ 【步骤2】_notes_to_packets(relevant_notes)
│   │
│   └─→ 为每个笔记创建 ContextPacket
│       ├─→ content = f"[笔记:{note['title']}]\n{note['content']}"
│       ├─→ timestamp = datetime.fromisoformat(note['updated_at'])
│       ├─→ token_count = len(content) // 4  # 简单估算
│       ├─→ relevance_score = 0.75  # 固定相关性
│       └─→ metadata = {
│               "type": "note",
│               "note_type": note['type'],
│               "note_id": note['note_id']
│           }
│       └─→ 返回: List[ContextPacket]
│
├─→ 【步骤3】context_builder.build(...)
│   │
│   └─→ ContextBuilder.build() [GSSC 流水线]
│       │
│       ├─→ 【Gather】_gather(...)
│       │   │
│       │   ├─→ 添加系统指令包 (P0)
│       │   │   └─→ ContextPacket(content=system_instructions, metadata={"type": "instructions"})
│       │   │
│       │   ├─→ memory_tool.execute("search", query="(任务状态 OR 子目标 OR 结论 OR 阻塞)")
│       │   │   └─→ MemoryTool.execute()
│       │   │       ├─→ 从 WorkingMemoryStorage 搜索
│       │   │       └─→ 返回相关记忆
│       │   │
│       │   ├─→ memory_tool.execute("search", query=user_query)
│       │   │   └─→ MemoryTool.execute()
│       │   │       └─→ 返回与用户查询相关的记忆
│       │   │
│       │   ├─→ rag_tool.run({"action": "search", "query": user_query, "top_k": 5})
│       │   │   └─→ RAGTool.run()
│       │   │       ├─→ _load_index() → 加载向量索引
│       │   │       ├─→ 查询知识库向量
│       │   │       └─→ 返回相关文档片段
│       │   │
│       │   ├─→ 添加对话历史包 (P3)
│       │   │   └─→ ContextPacket(content=history_text, metadata={"type": "history"})
│       │   │
│       │   └─→ 添加额外包 (笔记)
│       │       └─→ packets.extend(additional_packets)
│       │
│       ├─→ 【Select】_select(packets, user_query)
│       │   │
│       │   ├─→ 计算相关性分数 (关键词重叠)
│       │   ├─→ 计算新近性分数 (exp(-Δt / 3600))
│       │   ├─→ 计算复合分: 0.7 * relevance + 0.3 * recency
│       │   ├─→ 分离系统指令包 (固定纳入)
│       │   ├─→ 过滤: relevance_score >= min_relevance (0.3)
│       │   └─→ 按token预算填充 (max_tokens * (1 - reserve_ratio))
│       │
│       ├─→ 【Structure】_structure(selected_packets, user_query, system_instructions)
│       │   │
│       │   ├─→ [Role & Policies] - 系统指令
│       │   ├─→ [Task] - 用户问题
│       │   ├─→ [State] - 任务状态记忆
│       │   ├─→ [Evidence] - 事实证据 (RAG + 笔记)
│       │   ├─→ [Context] - 对话历史
│       │   └─→ [Output] - 输出约束
│       │
│       └─→ 【Compress】_compress(structured_context)
│           │
│           ├─→ count_tokens(context) → tiktoken encoding
│           ├─→ if current_tokens <= available_tokens: return context
│           └─→ 按段落截断压缩
│
├─→ 【步骤4】llm.invoke(messages)
│   │
│   ├─→ messages = [
│   │       {"role": "system", "content": context},  # GSSC 构建的上下文
│   │       {"role": "user", "content": user_input}
│   │   ]
│   │
│   └─→ HelloAgentsLLM.invoke()
│       └─→ openai.chat.completions.create()
│           └─→ 返回 LLM 响应
│
├─→ 【步骤5】_save_as_note(user_input, response)  # note_as_action=True
│   │
│   ├─→ 判断笔记类型
│   │   ├─→ if "问题" in user_input or "阻塞" in user_input: note_type = "blocker"
│   │   ├─→ elif "计划" in user_input or "下一步" in user_input: note_type = "action"
│   │   └─→ else: note_type = "conclusion"
│   │
│   └─→ note_tool.run({
│           "action": "create",
│           "title": f"{user_input[:30]}...",
│           "content": f"## 问题\n{user_input}\n\n## 分析\n{response}",
│           "note_type": note_type,
│           "tags": [self.project_name, "auto_generated"]
│       })
│       └─→ NoteTool.run() → _create_note()
│           ├─→ _generate_note_id() → "note_20260311_120000_0"
│           ├─→ 创建笔记对象
│           │   └─→ {
│           │         "id": note_id,
│           │         "title": title,
│           │         "content": content,
│           │         "type": note_type,
│           │         "tags": tags,
│           │         "created_at": now,
│           │         "updated_at": now
│           │       }
│           ├─→ _note_to_markdown(note) → Markdown + YAML frontmatter
│           │   └─→ """
│           │       ---
│           │       id: note_20260311_120000_0
│           │       title: 我们已经完成了数据模型层...
│           │       type: action
│           │       tags: ["data_pipeline_refactoring", "auto_generated"]
│           │       created_at: 2026-03-11T12:00:00
│           │       updated_at: 2026-03-11T12:00:00
│           │       ---
│           │
│           │       # 我们已经完成了数据模型层...
│           │
│           │       ## 问题
│           │       我们已经完成了数据模型层的重构...
│           │
│           │       ## 分析
│           │       [LLM response]
│           │       """
│           ├─→ 写入文件: workspace / "{note_id}.md"
│           ├─→ 更新索引: notes_index.json
│           │   └─→ {"notes": [...], "metadata": {"total_notes": 1}}
│           └─→ 返回: "✅ 笔记创建成功\nID: note_20260311_120000_0"
│
├─→ 【步骤6】_update_history(user_input, response)
│   │
│   ├─→ from tiny_agents.core.message import Message
│   ├─→ conversation_history.append(Message(user_input, "user", timestamp=now))
│   ├─→ conversation_history.append(Message(response, "assistant", timestamp=now))
│   ├─→ if len(conversation_history) > 10:
│   │   └─→ conversation_history = conversation_history[-10:]
│   └─→ 返回: response
│
└─→ 返回: str (LLM 响应)
```

---

## 阶段三：第二次交互 (`run()` with `note_as_action=False`)

### 调用链差异

第二次交互时，`note_as_action=False`，因此：

1. **不会** 执行 `_save_as_note()`
2. **会** 检索到第一次交互创建的笔记（因为笔记已保存）
3. **会** 使用检索到的笔记作为上下文

### 关键数据流

```
用户查询: "在重构业务逻辑层时,我遇到了依赖版本冲突的问题,该如何解决?"
    ↓
_retrieve_relevant_notes("...")
    ↓
note_tool.run({"action": "list", "note_type": "blocker", "limit": 2})
    → 无 blocker 笔记
    ↓
note_tool.run({"action": "search", "query": "重构业务逻辑层 依赖版本冲突", "limit": 3})
    → 找到第一次保存的 action 笔记!
    → {
         "note_id": "note_20260311_120000_0",
         "title": "我们已经完成了数据模型层...",
         "type": "action",
         "content": "## 问题\n我们已经完成了数据模型层的重构..."
       }
    ↓
_notes_to_packets([note])
    → ContextPacket(content="[笔记:我们已经完成了...]\n## 问题...", relevance_score=0.75)
    ↓
context_builder.build(..., additional_packets=[note_packet])
    → [Evidence] 包含历史笔记内容
    ↓
LLM 基于历史笔记回答问题
```

---

## 阶段四：查看笔记摘要

### 调用链图

```
assistant.note_tool.run({"action": "summary"})
│
└─→ NoteTool.run() → _get_summary()
    │
    ├─→ total = len(notes_index["notes"])
    │
    ├─→ 按类型统计
    │   ├─→ type_counts = {}
    │   └─→ for note in notes:
    │       type_counts[note["type"]] = type_counts.get(note["type"], 0) + 1
    │
    └─→ 返回摘要
        └─→ """
            📊 笔记摘要

            总笔记数: 1

            按类型统计:
              • action: 1
            """
```

---

## 核心组件交互图

```
┌─────────────────────────────────────────────────────────────────┐
│                    ProjectAssistant                              │
│                  (继承自 SimpleAgent)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐  │
│   │  MemoryTool   │    │   RAGTool     │    │   NoteTool    │  │
│   │  (工作记忆)    │    │  (知识库检索)  │    │  (结构化笔记)  │  │
│   └───────┬───────┘    └───────┬───────┘    └───────┬───────┘  │
│           │                    │                    │           │
│           └────────────────────┼────────────────────┘           │
│                                ▼                                │
│                      ┌───────────────┐                          │
│                      │ ContextBuilder│                          │
│                      │  (GSSC 流水线)  │                          │
│                      └───────┬───────┘                          │
│                               │                                  │
└───────────────────────────────┼──────────────────────────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │      SimpleAgent              │
                │  (基础对话Agent)               │
                │                               │
                │  构建 messages → LLM.invoke() │
                └───────────────────────────────┘
```

---

## NoteTool 内部流程详解

### 笔记存储结构

```
./data_pipeline_refactoring_notes/
│
├── notes_index.json          # 笔记索引
│   {
│     "notes": [
│       {
│         "id": "note_20260311_120000_0",
│         "title": "我们已经完成了数据模型层...",
│         "type": "action",
│         "tags": ["data_pipeline_refactoring", "auto_generated"],
│         "created_at": "2026-03-11T12:00:00"
│       }
│     ],
│     "metadata": {
│       "created_at": "2026-03-11T12:00:00",
│       "total_notes": 1
│     }
│   }
│
└── note_20260311_120000_0.md  # 笔记文件 (Markdown + YAML)
    ---
    id: note_20260311_120000_0
    title: 我们已经完成了数据模型层...
    type: action
    tags: ["data_pipeline_refactoring", "auto_generated"]
    created_at: 2026-03-11T12:00:00
    updated_at: 2026-03-11T12:00:00
    ---

    # 我们已经完成了数据模型层...

    ## 问题
    我们已经完成了数据模型层的重构,测试覆盖率达到85%。下一步计划重构业务逻辑层。

    ## 分析
    [LLM response here]
```

### NoteTool.run() 操作分发

```
NoteTool.run(parameters)
│
├─→ action == "create"  → _create_note()
│   ├─→ _generate_note_id()
│   ├─→ 创建笔记对象
│   ├─→ _note_to_markdown() → Markdown格式
│   ├─→ 写入 .md 文件
│   ├─→ 更新 notes_index.json
│   └─→ 返回: "✅ 笔记创建成功"
│
├─→ action == "read"    → _read_note()
│   ├─→ _get_note_path(note_id)
│   ├─→ 读取 .md 文件
│   ├─→ _markdown_to_note() → 解析YAML
│   └─→ _format_note() → 格式化输出
│
├─→ action == "update"  → _update_note()
│   ├─→ 读取现有笔记
│   ├─→ 更新字段
│   ├─→ 保存 .md 文件
│   └─→ 更新索引
│
├─→ action == "delete"  → _delete_note()
│   ├─→ 删除 .md 文件
│   └─→ 更新索引
│
├─→ action == "list"    → _list_notes()
│   ├─→ 按 note_type 过滤
│   ├─→ 应用 limit
│   └─→ 返回列表
│
├─→ action == "search"  → _search_notes()
│   ├─→ 遍历所有笔记
│   ├─→ 读取 .md 文件
│   ├─→ 检查标题/内容/标签匹配
│   └─→ 返回匹配结果
│
└─→ action == "summary" → _get_summary()
    ├─→ 统计总数
    └─→ 按类型分组统计
```

---

## 笔记类型说明

| 类型 | 用途 | 示例 |
|-----|------|-----|
| `task_state` | 任务状态跟踪 | "已完成数据模型重构，测试覆盖率85%" |
| `conclusion` | 关键结论 | "数据模型重构验证了分层架构的有效性" |
| `blocker` | 阻塞项/问题 | "依赖版本冲突导致测试失败" |
| `action` | 行动计划 | "下一步计划重构业务逻辑层" |
| `reference` | 参考资料 | "官方文档链接、技术方案参考" |
| `general` | 通用笔记 | "会议纪要、临时记录" |

---

## ContextBuilder GSSC 流水线

### 数据流

```
┌─────────────────────────────────────────────────────────────────┐
│                        Gather (收集)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  系统指令 ─────────────────────────────┐                        │
│  记忆检索 (MemoryTool.execute) ────────┤                        │
│  RAG检索 (RAGTool.run) ────────────────┼──→ ContextPacket[]     │
│  对话历史 ──────────────────────────────┤                        │
│  笔记包 (additional_packets) ──────────┘                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                        Select (筛选)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. 计算相关性: 关键词重叠度                                      │
│  2. 计算新近性: exp(-Δt / 3600)                                 │
│  3. 复合评分: 0.7 * 相关性 + 0.3 * 新近性                        │
│  4. 过滤: relevance >= min_relevance                            │
│  5. 按token预算填充                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Structure (结构化)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Role & Policies] - 系统指令                                    │
│  [Task] - 用户问题                                               │
│  [State] - 任务状态记忆                                          │
│  [Evidence] - RAG结果 + 笔记内容 ← 笔记在这里!                   │
│  [Context] - 对话历史                                            │
│  [Output] - 输出约束                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Compress (压缩)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  if token_count > available_tokens:                             │
│      按段落截断压缩                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    结构化上下文字符串
```

---

## 完整交互时序图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   用户      │     │  Assistant  │     │ ContextBuilder│    │  NoteTool   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                    │                    │                    │
       │ run("我们已经完成...")                    │                    │
       │───────────────────>│                    │                    │
       │                    │                    │                    │
       │                    │ _retrieve_notes()  │                    │
       │                    │───────────────────>│                    │
       │                    │                    │ run("search")      │
       │                    │                    │───────────────────>│
       │                    │                    │ _search_notes()    │
       │                    │                    │<───────────────────│
       │                    │ <───────────────────│                    │
       │                    │                    │                    │
       │                    │ _notes_to_packets() │                    │
       │                    │───────────────────>│                    │
       │                    │ <───────────────────│                    │
       │                    │                    │                    │
       │                    │ build(context)     │                    │
       │                    │───────────────────>│                    │
       │                    │ GSSC Pipeline      │                    │
       │                    │ <───────────────────│                    │
       │                    │                    │                    │
       │                    │ llm.invoke()       │                    │
       │                    │ (LLM处理)          │                    │
       │                    │                    │                    │
       │                    │ _save_as_note()    │                    │
       │                    │───────────────────>│                    │
       │                    │                    │ run("create")      │
       │                    │                    │───────────────────>│
       │                    │                    │ _create_note()     │
       │                    │                    │<───────────────────│
       │                    │ <───────────────────│                    │
       │                    │                    │                    │
       │ <───────────────────│                    │                    │
       │  response           │                    │                    │
       │                    │                    │                    │
┌──────┴──────┐     ┌──────┴──────┘     ┌──────┴──────┘     ┌──────┴──────┐
│   用户      │     │  Assistant  │     │ ContextBuilder│    │  NoteTool   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

---

## 关键文件位置

| 组件 | 文件路径 |
|-----|---------|
| ProjectAssistant | `tiny_agents/demo/contextbuilder_notetool_demo.py` |
| SimpleAgent | `tiny_agents/agents/simple_agent.py` |
| Agent (基类) | `tiny_agents/core/agent.py` |
| ContextBuilder | `tiny_agents/context/builder.py` |
| NoteTool | `tiny_agents/tools/builtin/note_tool.py` |
| MemoryTool | `tiny_agents/tools/builtin/memory_tool.py` |
| RAGTool | `tiny_agents/tools/builtin/rag_tool.py` |
| HelloAgentsLLM | `tiny_agents/core/llm.py` |
| Message | `tiny_agents/core/message.py` |

---

## 配置参数

### ContextConfig

```python
ContextConfig(
    max_tokens=4000,         # 总token预算
    reserve_ratio=0.15,      # 生成余量 (15%)
    min_relevance=0.3,       # 最小相关性阈值
    enable_mmr=True,         # 启用MMR多样性
    mmr_lambda=0.7,          # MMR平衡参数
    enable_compression=True  # 启用压缩
)
```

### NoteTool

```python
NoteTool(
    workspace="./data_pipeline_refactoring_notes",  # 笔记存储目录
    auto_backup=True,      # 自动备份
    max_notes=1000         # 最大笔记数
)
```

---

## 数据结构

### ContextPacket

```python
@dataclass
class ContextPacket:
    content: str                  # 信息内容
    timestamp: datetime           # 时间戳
    metadata: Dict[str, Any]      # 元信息
    token_count: int              # token数
    relevance_score: float        # 相关性 (0.0-1.0)
```

### Note (笔记对象)

```python
{
    "id": "note_20260311_120000_0",
    "title": "笔记标题",
    "content": "笔记内容",
    "type": "action",  # task_state, conclusion, blocker, action, reference, general
    "tags": ["project_name", "auto_generated"],
    "created_at": "2026-03-11T12:00:00",
    "updated_at": "2026-03-11T12:00:00",
    "metadata": {
        "word_count": 150,
        "status": "active"
    }
}
```

---

## 与 CodebaseMaintainer 的对比

| 特性 | ProjectAssistant (本Demo) | CodebaseMaintainer |
|-----|--------------------------|-------------------|
| Agent类型 | SimpleAgent | ReActAgent |
| 工具调用 | 无 (纯对话) | 有 (自主决策) |
| 笔记自动保存 | 支持 (`note_as_action`) | 无 |
| 终端能力 | 无 | 有 (TerminalTool) |
| 适用场景 | 长期项目助手 | 代码库维护 |

---

## 总结

`contextbuilder_notetool_demo.py` 展示了：

1. **ContextBuilder 与 NoteTool 的集成**：将笔记作为上下文包输入到 GSSC 流水线
2. **笔记驱动的对话**：通过检索历史笔记为 LLM 提供连贯的上下文
3. **自动笔记生成**：根据对话内容自动创建并保存笔记
4. **长期记忆能力**：结合 MemoryTool 和 NoteTool 实现跨会话记忆

核心价值在于展示了如何构建一个**有记忆的长期项目助手**，能够：
- 追踪项目进展
- 记录关键结论
- 基于历史笔记提供建议
- 自动积累项目知识
