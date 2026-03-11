# demo/contextbuilder_demo.py 详细完整代码执行调用链

## 文件概述

**文件路径**: `demo/contextbuilder_demo.py`

**核心功能**: 演示 ContextBuilder 的 GSSC (Gather-Select-Structure-Compress) 流水线，结合记忆工具和 RAG 工具构建上下文感知智能体

**主要组件**:
- `ContextBuilder` - GSSC 流水线实现
- `ContextAwareAgent` - 上下文感知智能体
- `MemoryTool` - 记忆管理工具
- `RAGTool` - 检索增强生成工具

---

# 整体架构图

```
contextbuilder_demo.py
    │
    ├── 导入模块
    │   ├── context.builder (ContextBuilder, ContextConfig)
    │   ├── core.llm (HelloAgentsLLM)
    │   ├── tools.builtin (MemoryTool, RAGTool)
    │   ├── agents (SimpleAgent)
    │   └── tools.registry (ToolRegistry)
    │
    ├── ContextAwareAgent 类定义
    │   ├── __init__() - 初始化
    │   ├── run() - 运行智能体
    │   └── 工具集成
    │       ├── MemoryTool
    │       ├── RAGTool
    │       └── ContextBuilder
    │
    └── 主程序入口
        ├── LLM 初始化
        ├── Agent 初始化
        └── 运行测试
```

---

# 测试用例 1: 上下文感知智能体查询

## 输入
```python
user_query = "如何优化Pandas的内存占用？"
```

## 完整代码执行调用链

### 阶段 1: 程序启动与导入

```
[SCRIPT START] python demo/contextbuilder_demo.py
│
├── [Line 1-7] 导入语句
│   ├── from tiny_agents.context.builder import ContextBuilder, ContextConfig
│   │   └── [context/builder.py] 执行导入
│   │       ├── ContextBuilder 类 [Line 74-423]
│   │       ├── ContextConfig 类 [Line 46-72]
│   │       ├── ContextPacket 类 [Line 22-44]
│   │       └── count_tokens 函数 [Line 414-422]
│   │
│   ├── from tiny_agents.core.llm import HelloAgentsLLM
│   │   └── [core/llm.py] 执行导入
│   │
│   ├── from tiny_agents.tools.builtin import MemoryTool, RAGTool
│   │   └── [tools/builtin/] 执行导入
│   │       ├── memory_tool.py [Line 1-481]
│   │       └── rag_tool.py [Line 1-878]
│   │
│   ├── from tiny_agents.agents import SimpleAgent
│   │   └── [agents/simple_agent.py] 执行导入
│   │
│   └── from tiny_agents.tools.registry import ToolRegistry
│       └── [tools/registry.py] 执行导入
│
├── [Line 9-58] ContextAwareAgent 类定义
│   │
│   └── [Line 61-72] if __name__ == "__main__": 条件判断
│       └── 条件: True (主程序执行)
│
└── 主程序开始执行
```

### 阶段 2: LLM 初始化

```
[Line 62] llm = HelloAgentsLLM()
│
└── [core/llm.py:30-74] HelloAgentsLLM.__init__() 执行流程
    │
    ├── [Line 30-74] __init__(self, model, api_key, base_url, provider, ...)
    │
    │   ├── [Line 55] self.model = model or os.getenv("LLM_MODEL_ID")
    │   │   ├── model = None (未传入)
    │   │   ├── os.getenv("LLM_MODEL_ID") → 检查环境变量
    │   │   └── 假设返回: "GLM-4.7" 或 "deepseek-chat" 等
    │   │
    │   ├── [Line 56] self.temperature = 0.7
    │   ├── [Line 57] self.max_tokens = None
    │   ├── [Line 58] self.timeout = 60
    │   │
    │   ├── [Line 62] self.provider = provider or self._auto_detect_provider(api_key, base_url)
    │   │   └── [llm.py:76-160] _auto_detect_provider() 执行流程
    │   │       ├── 检查环境变量
    │   │       │   ├── os.getenv("OPENAI_API_KEY") → None
    │   │       │   ├── os.getenv("DEEPSEEK_API_KEY") → 可能存在
    │   │       │   ├── os.getenv("ZHIPU_API_KEY") → 可能存在
    │   │       │   └── ... (检查其他提供商)
    │   │       │
    │   │       ├── 根据检测到的提供商返回
    │   │       │   └── 假设返回: "zhipu" 或 "deepseek"
    │   │
    │   │   └── [Line 160] return provider
    │   │
    │   ├── [Line 65] self.api_key, self.base_url = self._resolve_credentials(api_key, base_url)
    │   │   └── [llm.py:162-213] _resolve_credentials() 执行流程
    │   │       ├── 根据 provider 选择对应的环境变量
    │   │       │   ├── "zhipu" → ZHIPU_API_KEY + "https://open.bigmodel.cn/api/paas/v4"
    │   │       │   ├── "deepseek" → DEEPSEEK_API_KEY + "https://api.deepseek.com"
    │   │       │   └── ... (其他提供商)
    │   │       │
    │   │       └── 返回 (api_key, base_url)
    │   │
    │   ├── [Line 69-70] if not self.model: self.model = self._get_default_model()
    │   │   └── [llm.py:223-264] _get_default_model() 执行流程
    │   │       ├── 根据 provider 返回默认模型
    │   │       │   ├── "zhipu" → "glm-4.7"
    │   │       │   ├── "deepseek" → "deepseek-chat"
    │   │       │   └── ... (其他提供商)
    │   │       │
    │   │       └── 返回默认模型名称
    │   │
    │   └── [Line 74] self._client = self._create_client()
    │       └── [llm.py:215-221] _create_client() 执行流程
    │           ├── from openai import OpenAI
    │           └── return OpenAI(
    │               api_key=self.api_key,
    │               base_url=self.base_url,
    │               timeout=self.timeout
    │           )
    │           └── 返回 OpenAI 客户端实例
    │
    └── 返回 HelloAgentsLLM 实例
        ├── self.model = "GLM-4.7" (或类似)
        ├── self.provider = "zhipu" (或类似)
        ├── self.api_key = "sk-xxxxx"
        ├── self.base_url = "https://..."
        └── self._client = OpenAI(...)
```

### 阶段 3: ContextAwareAgent 初始化

```
[Line 63-69] agent = ContextAwareAgent(
    name="数据分析顾问",
    llm=llm,
    system_prompt="你是一位资深的Python数据工程顾问。",
    user_id="user123",
    knowledge_base_path="./data_science_kb"
)
│
└── [demo/contextbuilder_demo.py:9-58] ContextAwareAgent.__init__() 执行流程
    │
    ├── [Line 10-14] super().__init__(name, llm, **kwargs)
    │   └── [agents/simple_agent.py:13-20] SimpleAgent.__init__() 执行流程
    │       └── [Line 20] super().__init__(name, llm, system_prompt, config)
    │           └── [core/agent.py:32-131] Agent.__init__() 执行流程
    │               │
    │               ├── [Line 40-42] 初始化基础属性
    │               │   ├── self.name = "数据分析顾问"
    │               │   ├── self.llm = llm (HelloAgentsLLM 实例)
    │               │   └── self.system_prompt = "你是一位资深的Python数据工程顾问。"
    │               │
    │               ├── [Line 43] self.config = config or Config()
    │               │   └── [core/config.py] Config() 实例化
    │               │       ├── context_window: 8192
    │               │       ├── compression_threshold: 0.8
    │               │       ├── min_retain_rounds: 2
    │               │       └── ... (其他配置)
    │               │
    │               ├── [Line 49-55] 初始化 HistoryManager
    │               │   └── [context/history.py] HistoryManager() 实例化
    │               │
    │               ├── [Line 57-62] 初始化 ObservationTruncator
    │               │   └── [context/truncator.py] ObservationTruncator() 实例化
    │               │
    │               ├── [Line 64-66] 初始化 TokenCounter
    │               │   └── [context/token_counter.py] TokenCounter() 实例化
    │               │
    │               ├── [Line 69-87] 初始化 TraceLogger (如果启用)
    │               │   └── config.trace_enabled = False → 跳过
    │               │
    │               ├── [Line 90-102] 初始化 SkillLoader (如果启用)
    │               │   └── config.skills_enabled = False → 跳过
    │               │
    │               ├── [Line 105-131] 初始化 SessionStore (如果启用)
    │               │   └── config.session_enabled = False → 跳过
    │               │
    │               └── 返回 Agent 基类实例
    │
    │   ├── [Line 15] self.memory_tool = MemoryTool(user_id=kwargs.get("user_id", "default"))
    │   │   └── [tools/builtin/memory_tool.py:23-49] MemoryTool.__init__() 执行流程
    │   │       │
    │   │       ├── [Line 29-32] super().__init__(
    │   │       │       name="memory",
    │   │       │       description="记忆工具 - 可以存储和检索对话历史、知识和经验"
    │   │       │   )
    │   │       │   └── [tools/base.py:67-77] Tool.__init__() 执行流程
    │   │       │       ├── self.name = "memory"
    │   │       │       ├── self.description = "记忆工具..."
    │   │       │       └── self.expandable = False
    │   │       │
    │   │       ├── [Line 35] self.memory_config = memory_config or MemoryConfig()
    │   │       │   └── [memory/config.py] MemoryConfig() 实例化
    │   │       │       ├── max_memories: 1000
    │   │       │       ├── consolidation_threshold: 0.7
    │   │       │       └── ... (其他配置)
    │   │       │
    │   │       ├── [Line 36] self.memory_types = ["working", "episodic", "semantic"]
    │   │       │
    │   │       ├── [Line 38-45] self.memory_manager = MemoryManager(...)
    │   │       │   └── [memory/manager.py] MemoryManager() 实例化
    │   │       │       ├── 初始化各类型记忆存储
    │   │       │       ├── working memory (工作记忆)
    │   │       │       ├── episodic memory (情景记忆)
    │   │       │       └── semantic memory (语义记忆)
    │   │       │
    │   │       ├── [Line 48] self.current_session_id = None
    │   │       └── [Line 49] self.conversation_count = 0
    │   │
    │   │   └── 返回 MemoryTool 实例
    │
    │   ├── [Line 16] self.rag_tool = RAGTool(knowledge_base_path=kwargs.get("knowledge_base_path", "./kb"))
    │   │   └── [tools/builtin/rag_tool.py:40-88] RAGTool.__init__() 执行流程
    │   │       │
    │   │       ├── [Line 48-51] super().__init__(
    │   │       │       name="rag",
    │   │       │       description="RAG工具 - 支持多格式文档检索增强生成..."
    │   │       │       )
    │   │       │
    │   │       ├── [Line 53] self.knowledge_base_path = "./data_science_kb"
    │   │       ├── [Line 54-55] self.qdrant_url = os.getenv("QDRANT_URL")
    │   │       ├── [Line 55-56] self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
    │   │       ├── [Line 56] self.collection_name = "rag_knowledge_base"
    │   │       ├── [Line 57] self.rag_namespace = "default"
    │   │       ├── [Line 58] self._pipelines: Dict[str, Dict[str, Any]] = {}
    │   │       │
    │   │       ├── [Line 60-61] os.makedirs(knowledge_base_path, exist_ok=True)
    │   │       │   └── 创建 ./data_science_kb 目录
    │   │       │
    │   │       ├── [Line 64] self._init_components()
    │   │       │   └── [rag_tool.py:66-88] _init_components() 执行流程
    │   │       │       │
    │   │       │       ├── [Line 70-76] default_pipeline = create_rag_pipeline(...)
    │   │       │       │   └── [memory/rag/pipeline.py] create_rag_pipeline() 执行流程
    │   │       │       │       ├── 初始化 Qdrant 客户端
    │   │       │       │       ├── 初始化 Embeddings 模型
    │   │       │       │       ├── 创建文档解析器
    │   │       │       │       ├── 创建向量存储
    │   │       │       │       └── 返回 RAG 管道字典
    │   │       │       │
    │   │       │       ├── [Line 76] self._pipelines[self.rag_namespace] = default_pipeline
    │   │       │       │   └── self._pipelines["default"] = {...}
    │   │       │       │
    │   │       │       ├── [Line 78-79] self.llm = HelloAgentsLLM()
    │   │       │       │   └── 创建新的 LLM 实例
    │   │       │       │
    │   │       │       ├── [Line 81] self.initialized = True
    │   │       │       └── [Line 82] print(f"✅ RAG工具初始化成功...")
    │   │       │       └── 输出: ✅ RAG工具初始化成功: namespace=default, collection=rag_knowledge_base
    │   │       │
    │   │       └── 返回 None (初始化完成)
    │   │
    │   │   └── 返回 RAGTool 实例
    │
    │   ├── [Line 17-21] self.context_builder = ContextBuilder(
    │       memory_tool=self.memory_tool,
    │       rag_tool=self.rag_tool,
    │       config=ContextConfig(max_tokens=kwargs.get("max_tokens", 4000))
    │   )
    │   │   └── [context/builder.py:93-103] ContextBuilder.__init__() 执行流程
    │   │       │
    │   │       ├── [Line 99] self.memory_tool = memory_tool (MemoryTool 实例)
    │   │       ├── [Line 100] self.rag_tool = rag_tool (RAGTool 实例)
    │   │       │
    │   │       ├── [Line 101] self.config = config or ContextConfig()
    │   │       │   └── [builder.py:46-72] ContextConfig 数据类实例化
    │   │       │       ├── max_tokens: int = 4000
    │   │       │       ├── reserve_ratio: float = 0.15
    │   │       │       ├── min_relevance: float = 0.3
    │   │       │       ├── enable_mmr: bool = True
    │   │       │       ├── mmr_lambda: float = 0.7
    │   │       │       ├── system_prompt_template: str = ""
    │   │       │       └── enable_compression: bool = True
    │   │       │
    │   │       ├── [Line 102] self._encoding = tiktoken.get_encoding("cl100k_base")
    │   │       │   └── 获取 tiktoken 编码器 (用于 token 计数)
    │   │       │
    │   │       └── 返回 ContextBuilder 实例
    │
    │   ├── [Line 23] self.conversation_history = []
    │   │   └── self.conversation_history = []
    │
    └── 返回 ContextAwareAgent 实例
        ├── name = "数据分析顾问"
        ├── llm = HelloAgentsLLM 实例
        ├── system_prompt = "你是一位资深的Python数据工程顾问。"
        ├── memory_tool = MemoryTool 实例
        ├── rag_tool = RAGTool 实例
        ├── context_builder = ContextBuilder 实例
        └── conversation_history = []
```

### 阶段 4: 执行智能体查询

```
[Line 71] response = agent.run("如何优化Pandas的内存占用？")
│
└── [demo/contextbuilder_demo.py:25-58] ContextAwareAgent.run() 执行流程
    │
    ├── [Line 30-34] optimized_context = self.context_builder.build(
    │       user_query=user_query,
    │       conversation_history=self.conversation_history,
    │       system_instructions=self.system_prompt
    │   )
    │   │
    │   └── [context/builder.py:104-143] ContextBuilder.build() 执行流程 (GSSC 流水线)
    │       │
    │       │=== 阶段 4.1: Gather (收集候选信息) ===
    │       │
    │       ├── [Line 123-128] packets = self._gather(...)
    │       │   └── [builder.py:145-237] _gather() 执行流程
    │       │       │
    │       │       ├── [Line 165] packets = []
    │       │       │
    │       │       │--- P0: 系统指令 ---
    │       │       │
    │       │       ├── [Line 168-172] if system_instructions:
    │       │       │   ├── system_instructions = "你是一位资深的Python数据工程顾问。"
    │       │       │   ├── packets.append(ContextPacket(
    │       │       │   │   content=system_instructions,
    │       │       │   │   metadata={"type": "instructions"}
    │       │       │   │   ))
    │       │       │   │   └── [builder.py:22-44] ContextPacket.__init__() 执行流程
    │       │       │   │       ├── [Line 40-43] __post_init__()
    │       │       │   │       │   └── count_tokens(content)
    │       │       │   │       │       └── [builder.py:414-422] count_tokens() 执行
    │       │       │   │       │           ├── encoding.encode(content)
    │       │       │   │       │           └── 返回 token 数 (约 20-30 tokens)
    │       │       │   │       │
    │       │       │   │       └── self.token_count = token数
    │       │       │   │
    │       │       │   └── packets = [ContextPacket(content="你是一位资深的...", metadata={"type": "instructions"}, token_count=25, ...)]
    │       │       │
    │       │       │--- P1: 从记忆中获取任务状态 ---
    │       │       │
    │       │       ├── [Line 175-202] if self.memory_tool:
    │       │       │   ├── [Line 178-183] state_results = self.memory_tool.execute(...)
    │       │       │   │   └── [memory_tool.py:98-129] execute() 执行流程
    │       │       │   │       ├── action = "search"
    │       │       │   │       ├── query = "(任务状态 OR 子目标 OR 结论 OR 阻塞)"
    │       │       │   │       ├── min_importance = 0.7
    │       │       │   │       └── limit = 5
    │       │       │   │
    │       │       │   │   └── [Line 111] return self._search_memory(**kwargs)
    │       │       │   │       └── [memory_tool.py:183-252] _search_memory() 执行流程
    │       │       │   │           ├── [Line 201-207] results = self.memory_manager.retrieve_memories(...)
    │       │       │   │           │   └── [memory/manager.py] retrieve_memories() 执行流程
    │       │       │   │           │       ├── 搜索相关记忆
    │       │       │   │           │       ├── 按相关性排序
    │       │       │   │           │       └── 返回结果列表 (可能为空)
    │       │       │   │           │
    │       │       │   │           ├── [Line 209-230] if not results:
    │       │       │   │           │   ├── 首次运行，记忆为空
    │       │       │   │           │   └── 返回诊断信息
    │       │       │   │           │
    │       │       │   │           └── 返回 "🔍 未找到与 '...' 相关的记忆..."
    │       │       │   │
    │       │       │   ├── [Line 184-188] if state_results and "未找到" not in state_results:
    │       │       │   │   └── False (结果包含"未找到") → 跳过
    │       │       │   │
    │       │       │   ├── [Line 190-200] related_results = self.memory_tool.execute(...)
    │       │       │   │   └── 同上，搜索与当前查询相关的记忆
    │       │       │   │   └── 返回 "🔍 未找到相关记忆..."
    │       │       │   │
    │       │       │   └── [Line 191-200] if related_results and "未找到" not in related_results:
    │       │       │       └── False → 跳过
    │       │       │
    │       │       │--- P2: 从RAG中获取事实证据 ---
    │       │       │
    │       │       ├── [Line 205-218] if self.rag_tool:
    │       │       │   ├── [Line 207-211] rag_results = self.rag_tool.run({
    │       │       │   │   "action": "search",
    │       │       │   │   "query": user_query,
    │       │       │   │   "top_k": 5
    │       │       │   │   })
    │       │       │   │   └── [rag_tool.py:104-120] run() 执行流程
    │       │       │   │       ├── [Line 113] if not self.validate_parameters(parameters):
    │       │       │   │       │   └── 参数验证通过
    │       │       │   │       │
    │       │       │   │       ├── [Line 116] action = parameters.get("action")
    │       │       │   │       │   └── action = "search"
    │       │       │   │       │
    │       │       │   │       ├── [Line 120] return self.execute(action, **kwargs)
    │       │       │   │       │   └── [rag_tool.py:183-217] execute() 执行流程
    │       │       │   │           │
    │       │       │   │           ├── [Line 196] kwargs = self._preprocess_parameters(action, **kwargs)
    │       │       │   │           │   └── [rag_tool.py:218-246] _preprocess_parameters() 执行流程
    │       │       │   │               │   ├── 设置默认值
    │       │       │   │               │   │   ├── namespace: "default"
    │       │       │   │               │   │   ├── limit: 5
    │       │       │   │               │   │   ├── include_citations: True
    │       │       │   │               │   │   └── ... (其他默认值)
    │       │       │   │               │
    │       │       │   │               └── 返回处理后的 kwargs
    │       │       │   │
    │       │       │           ├── [Line 205] elif action == "search":
    │       │       │           │   └── [Line 206] return self._search(**kwargs)
    │       │       │           │       └── [rag_tool.py:326-381] _search() 执行流程
    │       │       │   │           ├── [Line 333] pipeline = self._get_pipeline(namespace)
    │       │       │   │           │   └── 获取 RAG 管道
    │       │       │   │           │
    │       │       │   │           ├── [Line 335-342] if enable_advanced_search:
    │       │       │   │           │   ├── results = pipeline["search_advanced"](
    │       │       │   │           │   │   query="如何优化Pandas的内存占用？",
    │       │       │   │           │   │   top_k=5,
    │       │       │   │           │   │   enable_mqe=True,
    │       │       │   │           │   │   enable_hyde=True
    │       │       │   │           │   │   )
    │       │       │   │           │   │   └── 执行向量搜索
    │       │       │   │           │   │       ├── 查询向量化
    │       │       │   │           │   │       ├── 相似度计算
    │       │       │   │           │   │       └── 返回 top-k 结果
    │       │       │   │           │   │
    │       │       │   │           │   └── results = [
    │       │       │   │           │       {
    │       │       │   │           │           "score": 0.85,
    │       │       │   │           │           "metadata": {
    │       │       │   │           │               "content": "Pandas 提供了多种优化内存的方法...",
    │       │       │   │           │               "source_path": "data_science_kb/pandas_optimization.md"
    │       │       │   │           │           }
    │       │       │   │           │       },
    │       │       │   │           │       ...
    │       │       │   │           │      ]
    │       │       │   │           │
    │       │       │   │           ├── [Line 350-351] if not results:
    │       │       │   │           │   └── False (有结果) → 跳过
    │       │       │   │           │
    │       │       │   │           ├── [Line 353-377] 格式化搜索结果
    │       │       │   │           │   └── 构建结果字符串
    │       │       │   │           │
    │       │       │   │           └── 返回搜索结果字符串
    │       │       │   │
    │       │       │   ├── [Line 212-216] if rag_results and "未找到" not in rag_results and "错误" not in rag_results:
    │       │       │   │   ├── rag_results = "搜索结果：\n\n1. 文档: **pandas_optimization.md** (相似度: 0.850)\n   ..."
    │       │       │   │   └── packets.append(ContextPacket(
    │       │       │   │       content=rag_results,
    │       │       │   │       metadata={"type": "knowledge_base"}
    │       │       │   │   │   ))
    │       │       │   │   │   └── 创建 ContextPacket
    │       │       │   │   │
    │       │       │   │   └── packets = [
    │       │       │           ContextPacket(content="你是一位资深的...", metadata={"type": "instructions"}),
    │       │       │           ContextPacket(content="搜索结果：...", metadata={"type": "knowledge_base"})
    │       │       │          ]
    │       │       │
    │       │       │--- P3: 对话历史 ---
    │       │       │
    │       │       ├── [Line 221-231] if conversation_history:
    │       │       │   ├── conversation_history = [] (首次运行)
    │       │       │   └── 跳过
    │       │       │
    │       │       ├── [Line 234] packets.extend(additional_packets)
    │       │       │   └── additional_packets = [] → 跳过
    │       │       │
    │       │       ├── [Line 235] print(f"🔍 [ContextBuilder] Gather阶段收集到 {len(packets)} 个候选上下文包")
    │       │       │   └── 输出: 🔍 [ContextBuilder] Gather阶段收集到 2 个候选上下文包
    │       │       │
    │       │       └── 返回 packets
    │       │
    │       │=== 阶段 4.2: Select (筛选与排序) ===
    │       │
    │       ├── [Line 131] selected_packets = self._select(packets, user_query)
    │       │   └── [builder.py:239-295] _select() 执行流程
    │       │       │
    │       │       │--- 1) 计算相关性 ---
    │       │       │
    │       │       ├── [Line 246-253] for packet in packets:
    │       │       │   ├── query_tokens = set("如何优化pandas的内存占用？".lower().split())
    │       │       │   │   └── {"如何", "优化", "pandas", "的", "内存", "占用？"}
    │       │       │   │
    │       │       │   ├── 第1个包: content="你是一位资深的Python数据工程顾问。"
    │       │       │   │   ├── content_tokens = {"你", "是", "一位", "资深的", "python", "数据", "工程", "顾问。"}
    │       │       │   │   ├── overlap = query_tokens & content_tokens = {"python"}
    │       │       │   │   ├── packet.relevance_score = 1/7 ≈ 0.143
    │       │       │   │
    │       │       │   ├── 第2个包: content="搜索结果：...Pandas 提供了多种优化内存的方法..."
    │       │       │   │   ├── content_tokens = {"搜索", "结果", "pandas", "提供了", "多种", "优化", "内存", "的", "方法"...}
    │       │       │   │   ├── overlap = query_tokens & content_tokens = {"pandas", "优化", "内存"}
    │       │       │   │   ├── packet.relevance_score = 3/7 ≈ 0.429
    │       │       │   │
    │       │       │   └── 相关性分数已计算
    │       │       │
    │       │       │--- 2) 计算新近性 ---
    │       │       │
    │       │       ├── [Line 256-259] def recency_score(ts: datetime) -> float:
    │       │       │   ├── delta = (datetime.now() - ts).total_seconds()
    │       │       │   ├── tau = 3600 (1小时时间尺度)
    │       │       │   └── return math.exp(-delta / tau)
    │       │       │       │
    │       │       ├── 对于刚创建的 ContextPacket (ts = datetime.now())
    │       │       │   ├── delta ≈ 0.001 秒
    │       │       │   └── recency_score ≈ 0.9999997 ≈ 1.0
    │       │       │
    │       │       │--- 3) 计算复合分 ---
    │       │       │
    │       │       ├── [Line 262-266] for p in packets:
    │       │       │   ├── rec = recency_score(p.timestamp) ≈ 1.0
    │       │       │   ├── score = 0.7 * p.relevance_score + 0.3 * rec
    │       │       │   │
    │       │       │   ├── 第1个包: score = 0.7 * 0.143 + 0.3 * 1.0 ≈ 0.1 + 0.3 = 0.4
    │       │       │   ├── 第2个包: score = 0.7 * 0.429 + 0.3 * 1.0 ≈ 0.3 + 0.3 = 0.6
    │       │       │   │
    │       │       │   └── scored_packets = [(0.4, 包1), (0.6, 包2)]
    │       │       │
    │       │       │--- 4) 分离系统包和普通包 ---
    │       │       │
    │       │       ├── [Line 269-271] 系统包和普通包分离
    │       │       │   ├── system_packets = [包1] (metadata.type == "instructions")
    │       │       │   ├── remaining = [包2] (其他包)
    │       │       │   │
    │       │       │   └── 按分数排序: remaining = [包2]
    │       │       │
    │       │       │--- 5) 过滤低相关性 ---
    │       │       │
    │       │       ├── [Line 274] filtered = [p for p in remaining if p.relevance_score >= self.config.min_relevance]
    │       │       ├── min_relevance = 0.3
    │       │       ├── 包2.relevance_score = 0.429 >= 0.3 → True
    │       │       │
    │       │       │   └── filtered = [包2]
    │       │       │
    │       │       │--- 6) 按预算填充 ---
    │       │       │
    │       │       ├── [Line 277] available_tokens = self.config.get_available_tokens()
    │       │       │   ├── available_tokens = int(4000 * (1 - 0.15)) = 3400
    │       │       │
    │       │       │   ├── [Line 278-292] 逐个添加包
    │       │       │   │
    │       │       │   ├── 先添加系统包
    │       │       │   │   ├── selected = [包1]
    │       │       │   │   ├── used_tokens = 包1.token_count ≈ 25
    │       │       │   │
    │       │       │   │   ├── 再添加其他包
    │       │       │   │   ├── selected = [包1, 包2]
    │       │       │   │   ├── used_tokens = 25 + 包2.token_count ≈ 25 + 500 = 525
    │       │       │   │
    │       │       │   │   └── 525 < 3400 → 未超预算，全部选中
    │       │       │   │
    │       │       │   ├── [Line 294] print(f"🔍 [ContextBuilder] Select阶段筛选出 {len(selected)} 个上下文包...")
    │       │       │   │   └── 输出: 🔍 [ContextBuilder] Select阶段筛选出 2 个上下文包, 共 525 个tokens
    │       │       │   │
    │       │       │   └── 返回 selected_packets
    │       │
    │       │=== 阶段 4.3: Structure (组织成结构化模板) ===
    │       │
    │       ├── [Line 134-138] structured_context = self._structure(
    │       │       selected_packets=selected_packets,
    │       │       user_query=user_query,
    │       │       system_instructions=system_instructions
    │       │   )
    │       │   └── [builder.py:329-382] _structure() 执行流程
    │       │       │
    │       │       ├── [Line 336] sections = []
    │       │       │
    │       │       │--- [Role & Policies] ---
    │       │       │
    │       │       ├── [Line 339-343] p0_packets = [p for p in selected_packets if p.metadata.get("type") == "instructions"]
    │       │       ├── p0_packets = [包1]
    │       │       ├── role_section = "[Role & Policies]\n你是一位资深的Python数据工程顾问。"
    │       │       ├── sections.append(role_section)
    │       │       │
    │       │       │--- [Task] ---
    │       │       │
    │       │       ├── [Line 346] sections.append(f"[Task]\n用户问题：{user_query}")
    │       │       ├── sections.append("[Task]\n用户问题：如何优化Pandas的内存占用？")
    │       │       │
    │       │       │--- [State] ---
    │       │       │
    │       │       ├── [Line 349-353] p1_packets = [p for p in selected_packets if p.metadata.get("type") == "task_state"]
    │       │       ├── p1_packets = [] (无任务状态记忆)
    │       │       └── 跳过
    │       │       │
    │       │       │--- [Evidence] ---
    │       │       │
    │       │       ├── [Line 356-364] p2_packets = [...]
    │       │       ├── p2_packets = [包2] (metadata.type == "knowledge_base")
    │       │       ├── evidence_section = "[Evidence]\n事实与引用：\n\n搜索结果：..."
    │       │       ├── sections.append(evidence_section)
    │       │       │
    │       │       │--- [Context] ---
    │       │       │
    │       │       ├── [Line 367-371] p3_packets = [p for p in selected_packets if p.metadata.get("type") == "history"]
    │       │       ├── p3_packets = [] (无对话历史)
    │       │       └── 跳过
    │       │       │
    │       │       │--- [Output] ---
    │       │       │
    │       │       ├── [Line 374-380] output_section = """[Output]
    │       │       请按以下格式回答：
    │       │       1. 结论（简洁明确）
    │       │       2. 依据（列出支撑证据及来源）
    │       │       3. 风险与假设（如有）
    │       │       4. 下一步行动建议（如适用）"""
    │       │       ├── sections.append(output_section)
    │       │       │
    │       │       ├── [Line 382] return "\n\n".join(sections)
    │       │       │
    │       │       └── structured_context =
    │       │           """
    │       │           [Role & Policies]
    │       │           你是一位资深的Python数据工程顾问。
    │       │
    │       │           [Task]
    │       │           用户问题：如何优化Pandas的内存占用？
    │       │
    │       │           [Evidence]
    │       │           事实与引用：
    │       │
    │       │           搜索结果：
    │       │
    │       │           1. 文档: **pandas_optimization.md** (相似度: 0.850)
    │       │              Pandas 提供了多种优化内存的方法...
    │       │
    │       │           [Output]
    │       │           请按以下格式回答：
    │       │           1. 结论（简洁明确）
    │       │           2. 依据（列出支撑证据及来源）
    │       │           3. 风险与假设（如有）
    │       │           4. 下一步行动建议（如适用）
    │       │           """
    │       │
    │       │=== 阶段 4.4: Compress (压缩与规范化) ===
    │       │
    │       ├── [Line 141] final_context = self._compress(structured_context)
    │       │   └── [builder.py:384-411] _compress() 执行流程
    │       │       │
    │       │       ├── [Line 386-387] if not self.config.enable_compression:
    │       │       │   └── enable_compression = True → 继续
    │       │       │
    │       │       ├── [Line 389] current_tokens = count_tokens(context)
    │       │       │   └── [builder.py:414-422] count_tokens() 执行流程
    │       │       │       ├── encoding = tiktoken.get_encoding("cl100k_base")
    │       │       │       ├── return len(encoding.encode(context))
    │       │       │       └── 返回 token 数 (约 150 tokens)
    │       │       │
    │       │       ├── [Line 390] available_tokens = self.config.get_available_tokens()
    │       │       │   └── available_tokens = 3400
    │       │       │
    │       │       ├── [Line 392-393] if current_tokens <= available_tokens:
    │       │       │   ├── 150 <= 3400 → True
    │       │       │   └── [Line 393] return context (未超预算，不压缩)
    │       │       │
    │       │       └── 返回 structured_context (未修改)
    │       │
    │       └── 返回 optimized_context
    │           └── 结构化的上下文字符串 (如上所示)
    │
    │=== 构建消息列表 ===
    │
    ├── [Line 36-39] messages = [
    │       {"role": "system", "content": optimized_context},
    │       {"role": "user", "content": user_query}
    │   ]
    │   └── messages = [
    │       {"role": "system", "content": "[Role & Policies]\n你是一位资深的Python数据工程顾问。\n\n..."},
    │       {"role": "user", "content": "如何优化Pandas的内存占用？"}
    │      ]
    │
    │=== 调用 LLM ===
    │
    ├── [Line 40] response = self.llm.invoke(messages)
    │   └── [core/llm.py:301-316] invoke() 执行流程
    │       │
    │       ├── [Line 307-313] response = self._client.chat.completions.create(
    │       │   ├── model=self.model → "GLM-4.7"
    │       │   ├── messages=messages
    │       │   ├── temperature=0.7
    │       │   └── max_tokens=None
    │       │
    │       │   └── OpenAI API 调用
    │       │       ├── POST https://open.bigmodel.cn/api/paas/v4/chat/completions
    │       │       ├── Headers: Authorization: Bearer sk-xxxxx
    │       │       └── Body: {"model": "GLM-4.7", "messages": [...], ...}
    │       │
    │       └── [Line 314] return response.choices[0].message.content
    │           └── LLM 生成回复
    │               示例:
    │               """
    │               1. 结论
    │               Pandas 优化内存有多种有效方法...
    │
    │               2. 依据
    │               根据知识库文档...
    │
    │               3. 风险与假设
    │               这些优化方法适用于大数据场景...

    │               4. 下一步行动建议
    │               建议根据具体数据集选择合适的优化策略...
    │               """
    │
    │=== 更新对话历史 ===
    │
    ├── [Line 42-49] from tiny_agents.core.message import Message
    │   └── 导入 Message 类
    │
    ├── [Line 44-46] self.conversation_history.append(
    │       Message(content=user_query, role="user", timestamp=datetime.now())
    │   )
    │   └── [core/message.py:9-24] Message.__init__() 执行流程
    │       ├── [Line 13] content: str = "如何优化Pandas的内存占用？"
    │       ├── [Line 14] role: str = "user"
    │       ├── [Line 15] timestamp: datetime = datetime.now()
    │       └── 返回 Message 实例
    │
    ├── [Line 47-49] self.conversation_history.append(
    │       Message(content=response, role="assistant", timestamp=datetime.now())
    │   )
    │   └── 同上，创建助手消息
    │
    │=== 记录到记忆系统 ===
    │
    ├── [Line 51-56] self.memory_tool.run({
    │       "action": "add",
    │       "content": f"Q: {user_query}\nA: {response}...",
    │       "memory_type": "episodic",
    │       "importance": 0.6
    │   })
    │   └── [memory_tool.py:51-67] run() 执行流程
    │       ├── [Line 60] if not self.validate_parameters(parameters):
    │       │   └── 参数验证通过
    │       │
    │       ├── [Line 63] action = parameters.get("action")
    │       │   └── action = "add"
    │       │
    │       ├── [Line 65-67] kwargs = {k: v for k, v in parameters.items() if k != "action"}
    │       │   └── kwargs = {
    │       │       "content": "Q: 如何优化Pandas的内存占用？\nA: ...",
    │       │       "memory_type": "episodic",
    │       │       "importance": 0.6
    │       │      }
    │       │
    │       └── [Line 67] return self.execute(action, **kwargs)
    │           └── [memory_tool.py:98-129] execute() 执行流程
    │               └── [Line 109] if action == "add":
    │                   └── [Line 110] return self._add_memory(**kwargs)
    │                       └── [memory_tool.py:131-169] _add_memory() 执行流程
    │                           ├── [Line 144-145] if self.current_session_id is None:
    │                           │   └── 生成会话 ID: "session_20260311_143025"
    │                           │
    │                           ├── [Line 158-164] memory_id = self.memory_manager.add_memory(...)
    │                           │   └── [memory/manager.py] add_memory() 执行流程
    │                           │       ├── 创建记忆对象
    │                           │       ├── 存储到对应类型的记忆库
    │                           │       └── 返回记忆 ID
    │                           │
    │                           ├── [Line 166] return f"✅ 记忆已添加 (ID: {memory_id[:8]}...)"
    │                           │
    │                           └── 返回 "✅ 记忆已添加 (ID: abc12345...)"
    │
    └── [Line 58] return response
        └── 返回 LLM 生成的回复字符串
```

### 阶段 5: 输出结果

```
[Line 72] print("智能体回复：", response)
    └── 输出: 智能体回复：1. 结论
        Pandas 优化内存有多种有效方法...

[SCRIPT END] 程序执行完毕
```

---

# 关键数据结构变化追踪

## ContextPacket 状态变化

```
# Gather 阶段后
packets = [
    ContextPacket(
        content="你是一位资深的Python数据工程顾问。",
        metadata={"type": "instructions"},
        token_count=25,
        relevance_score=0.143
    ),
    ContextPacket(
        content="搜索结果：\n\n1. 文档: **pandas_optimization.md**...",
        metadata={"type": "knowledge_base"},
        token_count=500,
        relevance_score=0.429
    )
]

# Select 阶段后 (计算复合分)
packets[0].relevance_score = 0.143
packets[1].relevance_score = 0.429
scored_packets = [(0.4, 包1), (0.6, 包2)]

# 最终选中
selected_packets = [包1, 包2]
```

## ContextBuilder 配置

```
ContextConfig {
    max_tokens: 4000,
    reserve_ratio: 0.15,
    min_relevance: 0.3,
    enable_mmr: True,
    mmr_lambda: 0.7,
    enable_compression: True
}

available_tokens = 4000 * (1 - 0.15) = 3400
```

## MemoryTool 状态

```
初始化:
{
    user_id: "user123",
    memory_types: ["working", "episodic", "semantic"],
    current_session_id: None,
    conversation_count: 0
}

首次运行后:
{
    current_session_id: "session_20260311_143025",
    conversation_count: 0
}

添加记忆后:
{
    conversation_count: 0 (未使用 auto_record_conversation)
}
```

## RAGTool 状态

```
初始化:
{
    knowledge_base_path: "./data_science_kb",
    collection_name: "rag_knowledge_base",
    rag_namespace: "default",
    _pipelines: {
        "default": {...}  # RAG 管道
    }
}
```

## 对话历史状态

```
初始化:
conversation_history = []

首次运行后:
conversation_history = [
    Message(content="如何优化Pandas的内存占用？", role="user", timestamp=...),
    Message(content="1. 结论\nPandas优化内存有多种有效方法...", role="assistant", timestamp=...)
]
```

---

# GSSC 流水线详细说明

## Gather (收集)

```
输入:
- user_query: "如何优化Pandas的内存占用？"
- conversation_history: []
- system_instructions: "你是一位资深的Python数据工程顾问。"

执行流程:
┌─────────────────────────────────────────┐
│ Gather: 收集候选信息                      │
├─────────────────────────────────────────┤
│ 1. P0: 系统指令 (强约束)                   │
│    ✅ 添加系统指令到 packets             │
│                                         │
│ 2. P1: 从记忆中获取任务状态               │
│    🔍 搜索任务状态记忆                     │
│    ❌ 未找到相关记忆                      │
│    🔍 搜索与查询相关的记忆                 │
│    ❌ 未找到相关记忆                      │
│                                         │
│ 3. P2: 从RAG中获取事实证据                │
│    ✅ 执行向量搜索                        │
│    ✅ 找到相关文档 (相似度: 0.85)         │
│    ✅ 添加到 packets                     │
│                                         │
│ 4. P3: 对话历史 (辅助材料)               │
│    ❌ 无历史记录                          │
│                                         │
│ 输出: 2 个候选上下文包                      │
└─────────────────────────────────────────┘
```

## Select (筛选)

```
输入:
- packets: [包1, 包2]
- user_query: "如何优化Pandas的内存占用？"

执行流程:
┌─────────────────────────────────────────┐
│ Select: 基于分数与预算的筛选                │
├─────────────────────────────────────────┤
│ 1. 计算相关性 (关键词重叠)                 │
│    包1: relevance = 0.143                 │
│    包2: relevance = 0.429                 │
│                                         │
│ 2. 计算新近性 (指数衰减)                   │
│    包1: recency ≈ 1.0                     │
│    包2: recency ≈ 1.0                     │
│                                         │
│ 3. 计算复合分 (0.7*相关性 + 0.3*新近性)     │
│    包1: score = 0.7*0.143 + 0.3*1.0 = 0.4  │
│    包2: score = 0.7*0.429 + 0.3*1.0 = 0.6  │
│                                         │
│ 4. 分离系统包和普通包                     │
│    系统包: [包1]                         │
│    普通包: [包2] (按分数排序)             │
│                                         │
│ 5. 过滤低相关性 (min_relevance=0.3)       │
│    包2: 0.429 >= 0.3 ✅                   │
│                                         │
│ 6. 按预算填充 (available=3400 tokens)   │
│    先添加系统包: 25 tokens               │
│    再添加其他包: 500 tokens              │
│    总计: 525 < 3400 ✅                   │
│                                         │
│ 输出: [包1, 包2] (全部选中)               │
└─────────────────────────────────────────┘
```

## Structure (组织)

```
输入:
- selected_packets: [包1, 包2]
- user_query: "如何优化Pandas的内存占用？"
- system_instructions: "你是一位资深的..."

执行流程:
┌─────────────────────────────────────────┐
│ Structure: 组织成结构化上下文模板          │
├─────────────────────────────────────────┤
│                                         │
│ [Role & Policies]                       │
│ 你是一位资深的Python数据工程顾问。      │
│                                         │
│ [Task]                                 │
│ 用户问题：如何优化Pandas的内存占用？      │
│                                         │
│ [Evidence]                             │
│ 事实与引用：                             │
│                                         │
│ 搜索结果：                              │
│ 1. 文档: **pandas_optimization.md**      │
│    Pandas 提供了多种优化内存的方法...     │
│                                         │
│ [Output]                               │
│ 请按以下格式回答：                       │
│ 1. 结论（简洁明确）                      │
│ 2. 依据（列出支撑证据及来源）             │
│ 3. 风险与假设（如有）                    │
│ 4. 下一步行动建议（如适用）               │
│                                         │
└─────────────────────────────────────────┘
```

## Compress (压缩)

```
输入:
- structured_context: (约 150 tokens)

执行流程:
┌─────────────────────────────────────────┐
│ Compress: 压缩与规范化                    │
├─────────────────────────────────────────┤
│                                         │
│ 1. 检查是否启用压缩                       │
│    enable_compression = True            │
│                                         │
│ 2. 计算 token 数                         │
│    current_tokens = 150                  │
│    available_tokens = 3400              │
│                                         │
│ 3. 检查是否超预算                         │
│    150 <= 3400 ✅                        │
│                                         │
│ 4. 未超预算，无需压缩                      │
│    返回原始上下文                         │
│                                         │
└─────────────────────────────────────────┘
```

---

# 执行时间线 (估算)

```
T0:      程序开始
T50:     导入模块完成
T100:    LLM 初始化完成
T500:    Agent 初始化开始
T550:    ├── MemoryTool 初始化
T600:    ├── RAGTool 初始化
T1200:   │   ├── Qdrant 连接
T1500:   │   └── RAG 管道创建
T1600:   └── ContextBuilder 初始化
T1650:   Agent 初始化完成

T2000:   agent.run() 开始
T2050:   ├─ ContextBuilder.build() 开始
T2100:   │   ├─ Gather 阶段
T2150:   │   │   ├─ 系统指令添加
T2200:   │   │   ├─ 记忆检索 (任务状态)
T2250:   │   │   │   └─ 未找到相关记忆
T2300:   │   │   ├─ 记忆检索 (相关记忆)
T2350:   │   │   │   └─ 未找到相关记忆
T2400:   │   │   ├─ RAG 检索
T2450:   │   │   │   ├─ 向量化查询
T2600:   │   │   │   ├─ 向量检索
T2800:   │   │   │   └─ 返回结果
T2850:   │   │   └─ Gather 完成 (2个包)
T2900:   │   │
T2950:   │   ├─ Select 阶段
T3000:   │   │   ├─ 计算相关性分数
T3050:   │   │   ├─ 计算新近性分数
T3100:   │   │   ├─ 计算复合分
T3150:   │   │   ├─ 按预算筛选
T3200:   │   │   └─ Select 完成 (2个包)
T3250:   │   │
T3300:   │   ├─ Structure 阶段
T3350:   │   │   ├─ 构建结构化模板
T3400:   │   │   └─ Structure 完成
T3450:   │   │
T3500:   │   └─ Compress 阶段
T3550:   │       ├─ 检查 token 预算
T3600:   │       └─ Compress 完成 (未超预算)
T3650:   │
T3700:   └─ optimized_context 准备完成

T3750:   ├─ 构建 messages
T3800:   ├─ 调用 LLM.invoke()
T4000:   │   └─ API 请求发送
T5000:   │   └─ API 响应接收
T5200:   │   └─ response 生成完成
T5250:   │
T5300:   ├─ 更新对话历史
T5350:   │   ├─ 添加用户消息
T5400:   │   └─ 添加助手消息
T5450:   │
T5500:   ├─ 记录到记忆系统
T5600:   │   └─ 记忆添加完成
T5650:   │
T5700:   └─ 返回 response

T5750:   输出结果
T5800: 程序结束
```

---

# 总结

## 核心流程

```
用户查询 "如何优化Pandas的内存占用？"
    │
    ▼
ContextBuilder.build() (GSSC 流水线)
    │
    ├─ Gather → 收集 2 个候选上下文包
    │   ├─ 系统指令
    │   └─ RAG 搜索结果
    │
    ├─ Select → 筛选出 2 个相关包
    │   ├─ 计算相关性分数
    │   ├─ 计算新近性分数
    │   └─ 按预算填充
    │
    ├─ Structure → 构建结构化上下文
    │   ├─ [Role & Policies]
    │   ├─ [Task]
    │   ├─ [Evidence]
    │   └─ [Output]
    │
    ├─ Compress → 检查预算 (150/3400 ✅)
    │
    └─ 返回优化后的上下文
        │
        ▼
    LLM.invoke() → 生成回复
        │
        ├─ 更新对话历史
        ├─ 记录到记忆系统
        │
        ▼
    返回最终回复
```

## 关键特性

| 特性 | 说明 |
|------|------|
| **GSSC 流水线** | Gather → Select → Structure → Compress |
| **多源信息融合** | 系统指令 + 记忆 + RAG + 历史记录 |
| **智能筛选** | 相关性 + 新近性 + 预算控制 |
| **结构化输出** | Role & Policies + Task + Evidence + Output |
| **记忆管理** | 自动记录对话到 episodic memory |

这份文档详细记录了 `demo/contextbuilder_demo.py` 的完整代码执行调用链，展示了 ContextBuilder 如何通过 GSSC 流水线构建优化的上下文。
