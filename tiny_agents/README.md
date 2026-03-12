# Tiny Agents

<div align="center">

**轻量级 AI Agent 框架 - 构建智能体的坚实基础**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个简洁而强大的 Python AI Agent 框架，提供多种 Agent 范式、丰富的工具系统、记忆管理、上下文工程和通信协议支持。

[快速开始](#快速开始) • [核心特性](#核心特性) • [架构概览](#架构概览) • [使用示例](#使用示例) • [API 文档](#api-文档)

</div>

---

## 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [Agent 类型](#agent-类型)
- [工具系统](#工具系统)
- [记忆系统](#记忆系统)
- [上下文工程](#上下文工程)
- [通信协议](#通信协议)
- [使用示例](#使用示例)
- [开发指南](#开发指南)
- [许可证](#许可证)

---

## 项目简介

Tiny Agents 是一个轻量级但功能完整的 AI Agent 框架，旨在为开发者提供构建智能应用的基础设施。框架设计遵循简洁性、可扩展性和实用性的原则，支持多种主流 LLM 提供商，提供丰富的开箱即用功能。

### 设计理念

- **简洁优先**: 清晰的 API 设计，最小化学习成本
- **范式丰富**: 支持多种 Agent 范式，适应不同场景
- **生产就绪**: 内置会话持久化、可观测性、错误处理等企业级特性
- **开放兼容**: 支持 OpenAI、DeepSeek、Qwen、Kimi、智谱等多种 LLM

---

## 核心特性

### 🤖 多种 Agent 范式

| Agent 类型 | 适用场景 | 特点 |
|-----------|---------|------|
| **SimpleAgent** | 简单对话 | 基础对话能力，支持历史管理 |
| **FunctionCallAgent** | 结构化任务 | 原生函数调用，类型安全 |
| **ReActAgent** | 推理行动 | 思考-行动循环，适合工具密集任务 |
| **PlanAndSolveAgent** | 复杂规划 | 分解规划，逐步执行 |
| **ReflectionAgent** | 迭代优化 | 自我反思，持续改进 |

### 🛠️ 丰富的工具系统

- **文件操作**: Read、Write、Edit、MultiEdit（支持乐观锁）
- **计算工具**: Calculator（安全表达式求值）
- **搜索工具**: Search（Web 搜索）
- **终端工具**: Terminal（命令执行）
- **笔记工具**: Note（结构化笔记）
- **记忆工具**: Memory（记忆检索）
- **RAG 工具**: RAG（检索增强生成）
- **任务工具**: Task（子代理机制）
- **进度工具**: TodoWrite（任务管理）
- **日志工具**: DevLog（开发日志）

### 🧠 分层记忆系统

```
┌─────────────────────────────────────┐
│     Memory Manager (协调层)          │
├─────────────────────────────────────┤
│  Working  │  Episodic  │ Semantic  │
│  Memory   │  Memory    │  Memory   │
├─────────────────────────────────────┤
│  Perceptual Memory (感知记忆)        │
├─────────────────────────────────────┤
│    Storage Layer (存储层)            │
│  SQLite │ Qdrant │ Neo4j │ Document │
└─────────────────────────────────────┘
```

### 📐 上下文工程

- **GSSC 流水线**: Gather → Select → Structure → Compress
- **智能压缩**: 基于阈值的自动压缩
- **Token 计数**: 缓存优化的增量计算
- **输出截断**: 工具输出智能截断

### 🌐 通信协议

- **MCP**: Model Context Protocol（模型上下文协议）
- **A2A**: Agent-to-Agent Protocol（智能体间通信）
- **ANP**: Agent Network Protocol（智能体网络发现）

### 📊 可观测性

- **Trace Logger**: JSONL + HTML 双格式记录
- **会话持久化**: 自动保存/恢复会话状态
- **生命周期钩子**: on_start、on_step、on_finish、on_error
- **熔断器**: 防止级联故障

---

## 项目结构

```
tiny_agents/
├── core/                   # 核心模块
│   ├── agent.py           # Agent 基类
│   ├── llm.py             # LLM 客户端
│   ├── config.py          # 配置管理
│   ├── message.py         # 消息定义
│   ├── lifecycle.py       # 生命周期管理
│   ├── streaming.py       # 流式输出
│   └── session_store.py   # 会话存储
│
├── agents/                 # Agent 实现
│   ├── simple_agent.py    # 简单对话
│   ├── function_call_agent.py  # 函数调用
│   ├── react_agent.py     # 推理行动
│   ├── plan_solve_agent.py    # 规划求解
│   ├── reflection_agent.py    # 反思优化
│   └── factory.py         # Agent 工厂
│
├── tools/                  # 工具系统
│   ├── base.py            # 工具基类
│   ├── registry.py        # 工具注册表
│   ├── response.py        # 工具响应
│   ├── errors.py          # 错误定义
│   ├── builtin/           # 内置工具
│   │   ├── calculator.py
│   │   ├── file_tools.py
│   │   ├── search_tool.py
│   │   ├── terminal_tool.py
│   │   ├── note_tool.py
│   │   ├── memory_tool.py
│   │   ├── rag_tool.py
│   │   ├── task_tool.py
│   │   ├── todowrite_tool.py
│   │   └── devlog_tool.py
│   └── chain.py           # 工具链
│
├── memory/                 # 记忆系统
│   ├── manager.py         # 记忆管理器
│   ├── base.py            # 基类定义
│   ├── types/             # 记忆类型
│   │   ├── working.py
│   │   ├── episodic.py
│   │   ├── semantic.py
│   │   └── perceptual.py
│   ├── storage/           # 存储后端
│   │   ├── document_store.py
│   │   ├── neo4j_store.py
│   │   └── qdrant_store.py
│   ├── rag/               # RAG 能力
│   │   ├── document.py
│   │   └── pipeline.py
│   └── embedding.py       # 嵌入模型
│
├── context/                # 上下文工程
│   ├── builder.py         # 上下文构建器
│   ├── history.py         # 历史管理
│   ├── truncator.py       # 输出截断
│   └── token_counter.py   # Token 计数
│
├── protocols/              # 通信协议
│   ├── mcp/               # MCP 协议
│   ├── a2a/               # A2A 协议
│   └── anp/               # ANP 协议
│
├── skills/                 # 知识外化
│   └── loader.py          # 技能加载器
│
├── observability/          # 可观测性
│   └── trace_logger.py    # 追踪日志
│
├── assistant/              # 助手示例
│   └── LearningAssistant/ # 学习助手
│
├── demo/                   # 演示脚本
├── tests/                  # 测试用例
└── __init__.py
```

---

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/tiny_agents.git
cd tiny_agents

# 安装依赖
pip install -r requirements.txt

# 或使用 pip 安装
pip install tiny-agents
```

### 环境配置

创建 `.env` 文件：

```bash
# OpenAI 配置
OPENAI_API_KEY=sk-xxx
LLM_MODEL_ID=gpt-4o-mini

# 或使用其他提供商
DEEPSEEK_API_KEY=sk-xxx
DASHSCOPE_API_KEY=sk-xxx
KIMI_API_KEY=sk-xxx
ZHIPU_API_KEY=sk-xxx

# 或使用通用配置
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_ID=gpt-4o-mini
```

### 第一个 Agent

```python
from tiny_agents.agents import SimpleAgent
from tiny_agents.core.llm import HelloAgentsLLM

# 初始化 LLM
llm = HelloAgentsLLM(
    model="gpt-4o-mini",
    provider="openai"
)

# 创建 Agent
agent = SimpleAgent(
    name="助手",
    llm=llm,
    system_prompt="你是一个友好的AI助手。"
)

# 运行对话
response = agent.run("你好，请介绍一下自己。")
print(response)
```

---

## 配置说明

### Config 配置类

```python
from tiny_agents.core.config import Config

config = Config(
    # LLM 配置
    default_model="gpt-4o-mini",
    default_provider="openai",
    temperature=0.7,
    max_tokens=2000,

    # 系统配置
    debug=False,
    log_level="INFO",

    # 上下文工程
    context_window=128000,
    compression_threshold=0.8,
    min_retain_rounds=10,
    enable_smart_compression=False,

    # 工具输出截断
    tool_output_max_lines=2000,
    tool_output_max_bytes=51200,
    tool_output_dir="tool-output",

    # 可观测性
    trace_enabled=True,
    trace_dir="memory/traces",
    trace_sanitize=True,

    # 会话持久化
    session_enabled=True,
    session_dir="memory/sessions",
    auto_save_enabled=False,
    auto_save_interval=10,

    # Skills 系统
    skills_enabled=True,
    skills_dir="skills",
    skills_auto_register=True,

    # 子代理机制
    subagent_enabled=True,
    subagent_max_steps=15,
)
```

---

## Agent 类型

### SimpleAgent - 简单对话

```python
from tiny_agents.agents import SimpleAgent
from tiny_agents.core.llm import HelloAgentsLLM

llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="对话助手",
    llm=llm,
    system_prompt="你是一个知识渊博的助手。"
)

response = agent.run("解释量子纠缠的基本原理。")
```

### FunctionCallAgent - 函数调用

```python
from tiny_agents.agents import FunctionCallAgent
from tiny_agents.tools import ToolRegistry, CalculatorTool

registry = ToolRegistry()
registry.register_tool(CalculatorTool())

agent = FunctionCallAgent(
    name="计算助手",
    llm=HelloAgentsLLM(),
    tool_registry=registry
)

response = agent.run("计算 123 * 456 + 789")
```

### ReActAgent - 推理行动

```python
from tiny_agents.agents import ReActAgent
from tiny_agents.tools import ToolRegistry, SearchTool

registry = ToolRegistry()
registry.register_tool(SearchTool())

agent = ReActAgent(
    name="研究助手",
    llm=HelloAgentsLLM(),
    tool_registry=registry,
    max_steps=5
)

response = agent.run("查找最新的 AI 发展趋势")
```

### PlanAndSolveAgent - 规划求解

```python
from tiny_agents.agents import PlanAndSolveAgent

agent = PlanAndSolveAgent(
    name="规划专家",
    llm=HelloAgentsLLM()
)

response = agent.run("制定一个学习 Python 的 4 周计划")
```

### ReflectionAgent - 反思优化

```python
from tiny_agents.agents import ReflectionAgent

agent = ReflectionAgent(
    name="代码审查员",
    llm=HelloAgentsLLM(),
    max_iterations=3
)

response = agent.run("编写一个快速排序算法的 Python 实现")
```

---

## 工具系统

### 使用内置工具

```python
from tiny_agents.tools import (
    ToolRegistry,
    ReadTool,
    WriteTool,
    EditTool,
    CalculatorTool,
    SearchTool
)

# 创建注册表
registry = ToolRegistry()

# 注册工具
registry.register_tool(CalculatorTool())
registry.register_tool(ReadTool(project_root="./"))
registry.register_tool(WriteTool(project_root="./"))
registry.register_tool(EditTool(project_root="./"))

# 列出工具
print(registry.list_tools())
# ['calculator', 'Read', 'Write', 'Edit']

# 获取工具描述
print(registry.get_tools_description())
```

### 创建自定义工具

```python
from tiny_agents.tools import Tool, ToolParameter, ToolResponse

class WeatherTool(Tool):
    """天气查询工具"""

    def __init__(self):
        super().__init__(
            name="weather",
            description="查询指定城市的天气情况",
            expandable=False
        )

    def get_parameters(self):
        return [
            ToolParameter(
                name="city",
                type="string",
                description="城市名称",
                required=True
            )
        ]

    def run(self, parameters):
        city = parameters.get("city")
        # 实现天气查询逻辑
        return ToolResponse.success(
            text=f"{city}今天晴朗，温度 25°C"
        )

# 注册使用
registry.register_tool(WeatherTool())
```

---

## 记忆系统

### 记忆类型

```python
from tiny_agents.memory import (
    MemoryManager,
    WorkingMemory,
    EpisodicMemory,
    SemanticMemory,
    PerceptualMemory
)

# 工作记忆 - 临时存储
working = WorkingMemory(max_items=100)
working.add("当前任务: 完成项目文档")

# 情景记忆 - 对话历史
episodic = EpisodicMemory()
episodic.add_episode(
    role="user",
    content="请帮我写一个排序算法",
    metadata={"timestamp": "2024-01-01"}
)

# 语义记忆 - 知识存储
semantic = SemanticMemory()
semantic.add_knowledge(
    content="Python 是一种高级编程语言",
    embedding=[0.1, 0.2, ...]  # 向量嵌入
)

# 感知记忆 - 多模态输入
perceptual = PerceptualMemory()
perceptual.add_perception(
    modality="image",
    data="base64_encoded_image",
    metadata={"source": "user_upload"}
)
```

### 记忆管理器

```python
from tiny_agents.memory import MemoryManager

manager = MemoryManager()

# 添加记忆
manager.add_working("当前任务: 编写测试")
manager.add_episodic("用户询问了 API 使用方法")
manager.add_semantic("FastAPI 是一个现代 Web 框架", embedding)

# 检索记忆
working_memories = manager.get_working_memory()
episodic_memories = manager.get_episodic_memory()
related_knowledge = manager.search_semantic("Python Web 框架")
```

---

## 上下文工程

### GSSC 流水线

```python
from tiny_agents.context import ContextBuilder, ContextConfig

config = ContextConfig(
    context_window=128000,
    compression_threshold=0.8,
    min_retain_rounds=10
)

builder = ContextBuilder(config)

# 构建上下文包
context_packet = builder.build(
    system_prompt="你是一个编程助手",
    conversation_history=history,
    user_input="如何使用 FastAPI？",
    additional_context=[...]
)

print(f"Token 数量: {context_packet.token_count}")
print(f"是否压缩: {context_packet.is_compressed}")
```

### 历史压缩

```python
from tiny_agents.context import HistoryManager

manager = HistoryManager(
    min_retain_rounds=10,
    compression_threshold=0.8
)

# 添加消息
for msg in messages:
    manager.append(msg)

# 检查是否需要压缩
if manager.should_compress():
    summary = manager.generate_summary()
    manager.compress(summary)

# 获取压缩后的历史
compressed_history = manager.get_history()
```

---

## 通信协议

### MCP 协议

```python
from tiny_agents.protocols import MCPServer, MCPClient

# 创建 MCP 服务器
server = MCPServer(name="my-tool-server")

@server.tool()
def search_database(query: str) -> str:
    """搜索数据库"""
    return f"搜索结果: {query}"

# 启动服务器
server.run()

# 连接到 MCP 服务器
client = MCPClient(uri="http://localhost:8000")
context = client.create_context("用户请求")
```

### A2A 协议

```python
from tiny_agents.protocols import A2AServer, A2AClient, AgentNetwork

# 创建 A2A 服务器
server = A2AServer(agent_id="agent-1")

@server.handler(message_type="query")
def handle_query(message):
    return {"response": "处理结果"}

server.start()

# 创建智能体网络
network = AgentNetwork()
network.register_agent("agent-1", "http://localhost:8001")
network.register_agent("agent-2", "http://localhost:8002")

# 发送消息
response = network.send_message(
    from_agent="agent-1",
    to_agent="agent-2",
    message_type="query",
    content={"query": "数据"}
)
```

### ANP 协议

```python
from tiny_agents.protocols import ANPDiscovery, ANPNetwork

# 服务发现
discovery = ANPDiscovery()

# 注册服务
discovery.register_service(
    service_id="search-service",
    service_type="search",
    endpoint="http://localhost:9000",
    capabilities=["web_search", "image_search"]
)

# 发现服务
services = discovery.discover_services(service_type="search")

# 创建网络
network = ANPNetwork()
network.connect_to_services(services)
```

---

## 使用示例

### 示例 1: 带工具的对话 Agent

```python
from tiny_agents.agents import FunctionCallAgent
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.tools import ToolRegistry, CalculatorTool, SearchTool

# 创建工具注册表
registry = ToolRegistry()
registry.register_tool(CalculatorTool())
registry.register_tool(SearchTool())

# 创建 Agent
agent = FunctionCallAgent(
    name="智能助手",
    llm=HelloAgentsLLM(),
    tool_registry=registry
)

# 对话
response = agent.run("帮我搜索 Python 教程，然后计算如果有 50 个学生，每人需要 2 本教材，总共需要多少本？")
print(response)
```

### 示例 2: 代码审查 Agent

```python
from tiny_agents.agents import ReflectionAgent
from tiny_agents.core.llm import HelloAgentsLLM

agent = ReflectionAgent(
    name="代码审查专家",
    llm=HelloAgentsLLM(),
    max_iterations=3,
    custom_prompts={
        "initial": "请编写一个二分查找算法的 Python 实现",
        "reflect": "审查以上代码，找出可能的 bug 和改进点",
        "refine": "根据反馈意见改进代码"
    }
)

code = agent.run("开始代码审查")
print(code)
```

### 示例 3: 文件操作 Agent

```python
from tiny_agents.agents import FunctionCallAgent
from tiny_agents.tools import ToolRegistry, ReadTool, WriteTool, EditTool
from tiny_agents.core.llm import HelloAgentsLLM

registry = ToolRegistry()
registry.register_tool(ReadTool(project_root="./my_project"))
registry.register_tool(WriteTool(project_root="./my_project"))
registry.register_tool(EditTool(project_root="./my_project"))

agent = FunctionCallAgent(
    name="文件助手",
    llm=HelloAgentsLLM(),
    tool_registry=registry
)

response = agent.run("读取 main.py 文件，将 print 语句改为 logging，然后保存")
print(response)
```

### 示例 4: 规划型 Agent

```python
from tiny_agents.agents import PlanAndSolveAgent
from tiny_agents.core.llm import HelloAgentsLLM

agent = PlanAndSolveAgent(
    name="学习规划师",
    llm=HelloAgentsLLM()
)

plan = agent.run("""
我想学习机器学习，请帮我制定一个 8 周的学习计划，
包括理论学习、实践项目和推荐的资源。
""")

print(plan)
```

### 示例 5: 多 Agent 协作

```python
from tiny_agents.agents import ReActAgent, FunctionCallAgent
from tiny_agents.tools import ToolRegistry, TaskTool
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.protocols import AgentNetwork

# 创建工具注册表
registry = ToolRegistry()

# 创建主 Agent
main_agent = FunctionCallAgent(
    name="主编排",
    llm=HelloAgentsLLM(),
    tool_registry=registry
)

# 注册子代理工具
task_tool = TaskTool(
    agent_factory=lambda agent_type: ReActAgent(
        name=f"子代理-{agent_type}",
        llm=HelloAgentsLLM(),
        tool_registry=registry
    ),
    tool_registry=registry
)
registry.register_tool(task_tool)

# 执行任务
response = main_agent.run("""
我需要完成三个任务：
1. 搜索最新的 Python Web 框架
2. 对比 Flask 和 FastAPI 的优缺点
3. 根据对比结果给出推荐
""")

print(response)
```

---

## 开发指南

### 添加新的 Agent 类型

```python
from tiny_agents.core.agent import Agent
from tiny_agents.core.llm import HelloAgentsLLM

class CustomAgent(Agent):
    """自定义 Agent 实现"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: str = None,
        config: Config = None
    ):
        super().__init__(name, llm, system_prompt, config)
        # 自定义初始化逻辑

    def run(self, input_text: str, **kwargs) -> str:
        """实现自定义的运行逻辑"""
        # 1. 构建消息
        messages = self._build_messages(input_text)

        # 2. 调用 LLM
        response = self.llm.invoke(messages, **kwargs)

        # 3. 保存历史
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(response, "assistant"))

        return response

    def _build_messages(self, input_text: str):
        """构建消息列表"""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": input_text})
        return messages
```

### 添加自定义工具

```python
from tiny_agents.tools import Tool, ToolParameter, ToolResponse, ToolErrorCode

class CustomTool(Tool):
    """自定义工具"""

    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="工具描述",
            expandable=False
        )

    def get_parameters(self):
        return [
            ToolParameter(
                name="param1",
                type="string",
                description="参数描述",
                required=True
            ),
            ToolParameter(
                name="param2",
                type="integer",
                description="可选参数",
                required=False,
                default=10
            )
        ]

    def run(self, parameters):
        try:
            # 实现工具逻辑
            result = self._execute(parameters)
            return ToolResponse.success(
                text="执行成功",
                data={"result": result}
            )
        except Exception as e:
            return ToolResponse.error(
                code=ToolErrorCode.INTERNAL_ERROR,
                message=f"执行失败: {str(e)}"
            )

    def _execute(self, parameters):
        # 实际执行逻辑
        return "结果"
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_simple_agent.py

# 查看测试覆盖率
pytest --cov=tiny_agents tests/
```

---

## 相关文档

- [架构设计文档](docs/architecture.md)
- [API 参考手册](docs/api.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)

---

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 致谢

感谢所有为本项目做出贡献的开发者！

---

<div align="center">

**[⬆ 返回顶部](#tiny-agents)**

Made with ❤️ by the Tiny Agents Team

</div>
