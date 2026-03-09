# demo/test_react_agent.py 各测试用例详细完整调用链

## 文件概述

**文件路径**: `demo/test_react_agent.py`

**测试函数**:
- `test_react_agent()` - 基础功能测试（3个测试用例）
- `test_custom_prompt()` - 自定义提示词测试（1个测试用例）

---

## 整体调用链架构

```
test_react_agent.py (测试入口)
    │
    ├── HelloAgentsLLM (LLM客户端)
    │   └── core/llm.py
    │
    ├── ToolRegistry (工具注册表)
    │   └── tools/registry.py
    │
    ├── MyReActAgent (自定义ReAct Agent)
    │   └── demo/my_react_agent.py
    │       └── 继承自 ReActAgent
    │           └── agents/react_agent.py
    │               └── 继承自 Agent
    │                   └── core/agent.py
    │
    └── 工具实现
        ├── tools/builtin/calculator.py
        └── tools/builtin/search.py
```

---

# 测试用例 1: 数学计算问题

## 输入
```python
math_question = "请帮我计算：(25 + 15) * 3 - 8 的结果是多少？"
```

## 完整调用链

### 阶段 1: 初始化 (test_react_agent 函数)

```
test_react_agent() [第 10 行]
│
├── [第 8 行] load_dotenv()
│   └── 来源: dotenv 库
│   └── 功能: 从 .env 文件加载环境变量
│
├── [第 14 行] llm = HelloAgentsLLM()
│   └── 来源: tiny_agents/core/llm.py:18
│   │
│   ├── __init__() [第 30-74 行]
│   │   ├── [第 55 行] self.model = model or os.getenv("LLM_MODEL_ID")
│   │   ├── [第 62 行] self.provider = provider or self._auto_detect_provider(api_key, base_url)
│   │   │   └── _auto_detect_provider() [第 76-160 行]
│   │   │       ├── 检查环境变量: OPENAI_API_KEY, DEEPSEEK_API_KEY, etc.
│   │   │       ├── 根据API密钥格式判断
│   │   │       ├── 根据base_url判断
│   │   │       └── 返回检测到的提供商 (如 "deepseek", "openai", "zhipu")
│   │   │
│   │   ├── [第 65 行] self.api_key, self.base_url = self._resolve_credentials(api_key, base_url)
│   │   │   └── _resolve_credentials() [第 162-213 行]
│   │   │       ├── 根据 provider 选择对应的环境变量
│   │   │       │   ├── "openai" → OPENAI_API_KEY + "https://api.openai.com/v1"
│   │   │       │   ├── "deepseek" → DEEPSEEK_API_KEY + "https://api.deepseek.com"
│   │   │       │   ├── "zhipu" → ZHIPU_API_KEY + "https://open.bigmodel.cn/api/paas/v4"
│   │   │       │   └── ... (其他提供商)
│   │   │       └── 返回 (api_key, base_url)
│   │   │
│   │   ├── [第 69 行] if not self.model: self.model = self._get_default_model()
│   │   │   └── _get_default_model() [第 223-264 行]
│   │   │       ├── "openai" → "gpt-3.5-turbo"
│   │   │       ├── "deepseek" → "deepseek-chat"
│   │   │       ├── "zhipu" → "glm-4.7"
│   │   │       └── ... (其他提供商)
│   │   │
│   │   └── [第 74 行] self._client = self._create_client()
│   │       └── _create_client() [第 215-221 行]
│   │           └── return OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
│
├── [第 17 行] tool_registry = ToolRegistry()
│   └── 来源: tiny_agents/tools/registry.py:10
│   │
│   ├── __init__() [第 20-28 行]
│   │   ├── [第 21 行] self._tools: dict[str, Tool] = {}
│   │   ├── [第 22 行] self._functions: dict[str, dict] = {}
│   │   ├── [第 25 行] self.read_metadata_cache: Dict = {}
│   │   └── [第 28 行] self.circuit_breaker = circuit_breaker or CircuitBreaker()
│   │
│   └── CircuitBreaker 初始化
│       └── 来源: tiny_agents/tools/circuit_breaker.py
│       ├── failure_threshold: int = 5 (默认)
│       ├── timeout_seconds: int = 60 (默认)
│       └── _states: Dict[str, CircuitState] = {}
│
├── [第 24-25 行] 导入并注册计算器工具
│   │
│   ├── from tiny_agents.tools.builtin.calculator import calculate
│   │   └── 来源: tiny_agents/tools/builtin/calculator.py:145
│   │   └── def calculate(expression: str) -> str:
│   │       └── [第 155-156 行]
│   │           tool = CalculatorTool()
│   │           return tool.run({"input": expression})
│   │
│   └── tool_registry.register_function("calculate", "执行数学计算，支持基本的四则运算", calculate)
│       └── register_function() [registry.py 第 57-110 行]
│           ├── [第 84-87 行] 兼容旧调用方式
│           ├── [第 89-91 行] 自动提取名称
│           ├── [第 93-101 行] 自动提取描述
│           └── [第 106-110 行]
│               self._functions["calculate"] = {
│                   "description": "执行数学计算，支持基本的四则运算",
│                   "func": calculate
│               }
│
├── [第 32-33 行] 导入并注册搜索工具 (如果可用)
│   │
│   ├── from tiny_agents.tools.builtin.search import search
│   └── tool_registry.register_function("search", "搜索互联网信息", search)
│
└── [第 39-44 行] agent = MyReActAgent(...)
    └── 来源: tiny_agents/demo/my_react_agent.py:38
    │
    ├── __init__() [第 43-58 行]
    │   ├── [第 53 行] super().__init__(name, llm, system_prompt, config)
    │   │   └── → ReActAgent.__init__() [react_agent.py 第 52-80 行]
    │   │       └── → Agent.__init__() [agent.py 第 32-131 行]
    │   │           ├── [第 40-42 行] 初始化基础属性
    │   │           │   ├── self.name = "我的推理行动助手"
    │   │           │   ├── self.llm = llm
    │   │           │   └── self.system_prompt = None
    │   │           │
    │   │           ├── [第 43 行] self.config = config or Config()
    │   │           │   └── Config() 默认值:
    │   │           │       ├── context_window: 8192
    │   │           │       ├── compression_threshold: 0.8
    │   │           │       ├── min_retain_rounds: 2
    │   │           │       ├── tool_output_max_lines: 100
    │   │           │       └── ... (其他配置)
    │   │           │
    │   │           ├── [第 52-55 行] 初始化 HistoryManager
    │   │           │   └── 来源: tiny_agents/context/history.py
    │   │           │   ├── min_retain_rounds: 2
    │   │           │   └── compression_threshold: 0.8
    │   │           │
    │   │           ├── [第 57-62 行] 初始化 ObservationTruncator
    │   │           │   └── 来源: tiny_agents/context/truncator.py
    │   │           │   ├── max_lines: 100
    │   │           │   ├── max_bytes: 10000
    │   │           │   └── truncate_direction: "end"
    │   │           │
    │   │           ├── [第 66 行] 初始化 TokenCounter
    │   │           │   └── 来源: tiny_agents/context/token_counter.py
    │   │           │   └── model: self.llm.model
    │   │           │
    │   │           ├── [第 72-87 行] 初始化 TraceLogger (如果 config.trace_enabled)
    │   │           │
    │   │           ├── [第 94-102 行] 初始化 SkillLoader (如果 config.skills_enabled)
    │   │           │
    │   │           └── [第 109-131 行] 初始化 SessionStore (如果 config.session_enabled)
    │   │
    │   ├── [第 54 行] self.tool_registry = tool_registry
    │   ├── [第 55 行] self.max_steps = 5
    │   ├── [第 56 行] self.current_history = []
    │   └── [第 57 行] self.prompt_template = MY_REACT_PROMPT
```

### 阶段 2: 执行测试1 - 数学计算

```
[第 55 行] result1 = agent.run("请帮我计算：(25 + 15) * 3 - 8 的结果是多少？")
│
└── MyReActAgent.run() [my_react_agent.py 第 60 行]
    │
    ├── [第 62 行] self.current_history = []
    ├── [第 63 行] current_step = 0
    │
    └── while current_step < self.max_steps: [第 67 行]
        │
        │==== 第 1 步开始 ====
        │
        ├── [第 68 行] current_step = 1
        │
        │--- 构建提示词 ---
        ├── [第 72 行] tools_desc = self.tool_registry.get_tools_description()
        │   └── get_tools_description() [registry.py 第 222-239 行]
        │       ├── 遍历 self._tools (Tool 对象)
        │       │   └── descriptions.append(f"- {tool.name}: {tool.description}")
        │       └── 遍历 self._functions (函数工具)
        │           └── descriptions.append(f"- {name}: {info['description']}")
        │       返回:
        │       ```
        │       - calculate: 执行数学计算，支持基本的四则运算
        │       - search: 搜索互联网信息
        │       ```
        │
        ├── [第 73 行] history_str = "\n".join(self.current_history)
        │   └── 返回 "" (第一次循环，历史为空)
        │
        ├── [第 74-78 行] prompt = self.prompt_template.format(...)
        │   └── 填充 MY_REACT_PROMPT 模板:
        │       ```
        │       你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。
        │
        │       ## 可用工具
        │       - calculate: 执行数学计算，支持基本的四则运算
        │       - search: 搜索互联网信息
        │
        │       ## 工作流程
        │       请严格按照以下格式进行回应，每次只能执行一个步骤：
        │
        │       Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
        │       Action: 你决定采取的行动，必须是以下格式之一：
        │       - `{{tool_name}}[{{tool_input}}]` - 调用指定工具
        │       - `Finish[最终答案]` - 当你有足够信息给出最终答案时
        │
        │       ## 当前任务
        │       **Question:** 请帮我计算：(25 + 15) * 3 - 8 的结果是多少？
        │
        │       ## 执行历史
        │
        │       现在开始你的推理和行动：
        │       ```
        │
        │--- 调用 LLM ---
        ├── [第 81-82 行] response_text = self.llm.invoke(messages)
        │   └── invoke() [llm.py 第 301-316 行]
        │       ├── [第 307 行] response = self._client.chat.completions.create(
        │       │   model=self.model,
        │       │   messages=[{"role": "user", "content": prompt}],
        │       │   temperature=0.7,
        │       │   max_tokens=None
        │       │ )
        │       │   └── OpenAI API 调用
        │       │       ├── POST {base_url}/chat/completions
        │       │       ├── Headers: Authorization: Bearer {api_key}
        │       │       └── Body: {"model": ..., "messages": [...], ...}
        │       │
        │       └── [第 314 行] return response.choices[0].message.content
        │           └── LLM 可能的响应示例:
        │               ```
        │               Thought: 用户要求计算一个数学表达式 (25 + 15) * 3 - 8。我需要使用计算器工具来计算这个表达式。
        │               Action: calculate[(25 + 15) * 3 - 8]
        │               ```
        │
        │--- 解析输出 ---
        ├── [第 85 行] thought, action = self._parse_output(response_text)
        │   └── _parse_output() [my_react_agent.py 第 107-125 行]
        │       ├── [第 118 行] thought_match = re.search(r'Thought:\s*(.*?)(?=Action:|$)', response_text, re.DOTALL)
        │       │   └── 提取 Thought: "用户要求计算一个数学表达式..."
        │       └── [第 122 行] action_match = re.search(r'Action:\s*(.*)', response_text, re.DOTALL)
        │           └── 提取 Action: "calculate[(25 + 15) * 3 - 8]"
        │
        │--- 检查是否完成 ---
        ├── [第 88 行] if action and action.startswith("Finish"):
        │   └── False (action 是 "calculate[...]")
        │
        │--- 执行工具调用 ---
        ├── [第 96 行] tool_name, tool_input = self._parse_action(action)
        │   └── _parse_action() [my_react_agent.py 第 127-141 行]
        │       └── [第 138 行] match = re.match(r'(\w+)\[(.*)\]', action_text)
        │           └── 解析 "calculate[(25 + 15) * 3 - 8]"
        │               ├── tool_name = "calculate"
        │               └── tool_input = "(25 + 15) * 3 - 8"
        │
        ├── [第 97 行] observation = self.tool_registry.execute_tool(tool_name, tool_input)
        │   └── execute_tool() [registry.py 第 132-220 行]
        │       │
        │       ├── [第 144-153 行] 检查熔断器
        │       │   └── self.circuit_breaker.is_open("calculate")
        │       │       └── 返回 False (首次调用，熔断器关闭)
        │       │
        │       ├── [第 159-182 行] 查找 Tool 对象
        │       │   └── "calculate" 不在 self._tools 中
        │       │
        │       ├── [第 185-207 行] 查找函数工具
        │       │   └── [第 186 行] func = self._functions["calculate"]["func"]
        │       │       └── 返回 calculate 函数 [calculator.py:145]
        │       │
        │       ├── [第 187 行] start_time = time.time()
        │       │
        │       ├── [第 190 行] result = func("(25 + 15) * 3 - 8")
        │       │   └── calculate() [calculator.py 第 145-156 行]
        │       │       ├── [第 155 行] tool = CalculatorTool()
        │       │       │   └── CalculatorTool.__init__() [calculator.py 第 43-47 行]
        │       │       │       ├── name="python_calculator"
        │       │       │       └── description="执行数学计算。支持基本运算、数学函数等..."
        │       │       │
        │       │       └── [第 156 行] return tool.run({"input": "(25 + 15) * 3 - 8"})
        │       │           └── run() [calculator.py 第 49-102 行]
        │       │               ├── [第 60 行] expression = "(25 + 15) * 3 - 8"
        │       │               ├── [第 62-66 行] 检查表达式是否为空
        │       │               ├── [第 68 行] print("🧮 正在计算: (25 + 15) * 3 - 8")
        │       │               ├── [第 70-73 行] 解析并计算表达式
        │       │               │   ├── node = ast.parse("(25 + 15) * 3 - 8", mode='eval')
        │       │               │   └── result = self._eval_node(node.body)
        │       │               │       └── _eval_node() [calculator.py 第 104-130 行]
        │       │               │           ├── 递归计算 AST 节点
        │       │               │           ├── ast.BinOp: operator.add(25, 15) = 40
        │       │               │           ├── ast.BinOp: operator.mul(40, 3) = 120
        │       │               │           └── ast.BinOp: operator.sub(120, 8) = 112
        │       │               │
        │       │               ├── [第 74 行] result_str = "112"
        │       │               ├── [第 76 行] print("✅ 计算结果: 112")
        │       │               └── [第 78-86 行] 返回 ToolResponse.success()
        │       │                   └── ToolResponse 对象:
        │       │                       ├── text: "计算结果: 112"
        │       │                       ├── status: ToolStatus.SUCCESS
        │       │                       └── data: {"result": 112, ...}
        │       │
        │       ├── [第 191 行] elapsed_ms = int((time.time() - start_time) * 1000)
        │       │
        │       ├── [第 194-199 行] 包装为 ToolResponse
        │       │   └── ToolResponse.success(
        │       │       text="计算结果: 112",
        │       │       data={"output": ToolResponse(text="计算结果: 112", status=SUCCESS, ...)},
        │       │       stats={"time_ms": elapsed_ms},
        │       │       context={"tool_name": "calculate", "input": "(25 + 15) * 3 - 8"}
        │       │   )
        │       │
        │       └── [第 218 行] self.circuit_breaker.record_result("calculate", response)
        │           └── 记录成功，熔断器保持 CLOSED 状态
        │
        │--- 记录历史 ---
        ├── [第 98 行] self.current_history.append("Action: calculate[(25 + 15) * 3 - 8]")
        └── [第 99 行] self.current_history.append("Observation: 计算结果: 112")
            └── current_history = [
                "Action: calculate[(25 + 15) * 3 - 8]",
                "Observation: 计算结果: 112"
            ]

        │==== 第 2 步开始 ====
        │
        ├── [第 68 行] current_step = 2
        │
        │--- 构建提示词 (包含历史) ---
        ├── [第 72-78 行] prompt = self.prompt_template.format(...)
        │   └── history_str =
        │       ```
        │       Action: calculate[(25 + 15) * 3 - 8]
        │       Observation: 计算结果: 112
        │       ```
        │
        │--- 调用 LLM ---
        ├── [第 81-82 行] response_text = self.llm.invoke(messages)
        │   └── LLM 可能的响应:
        │       ```
        │       Thought: 计算器已经返回了结果，(25 + 15) * 3 - 8 = 112。现在我有足够的信息来回答用户的问题。
        │       Action: Finish[计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。]
        │       ```
        │
        │--- 解析输出 ---
        ├── [第 85 行] thought, action = self._parse_output(response_text)
        │   ├── thought = "计算器已经返回了结果..."
        │   └── action = "Finish[计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。]"
        │
        │--- 检查是否完成 ---
        ├── [第 88-92 行] if action and action.startswith("Finish"):
        │   ├── [第 89 行] final_answer = self._parse_action_input(action)
        │   │   └── _parse_action_input() [my_react_agent.py 第 143-154 行]
        │   │       └── [第 153 行] match = re.match(r'\w+\[(.*)\]', action_text)
        │   │           └── 解析 "Finish[计算结果是 112...]"
        │   │           └── 返回 "计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。"
        │   │
        │   ├── [第 90 行] self.add_message(Message("请帮我计算：(25 + 15) * 3 - 8 的结果是多少？", "user"))
        │   │   └── add_message() [agent.py 第 300-320 行]
        │   │       ├── [第 305 行] history_manager.append(message)
        │   │       ├── [第 308 行] self._history_token_count += token_counter.count_message(message)
        │   │       ├── [第 312-313 行] if self._should_compress(): self._compress_history()
        │   │       └── [第 316-319 行] if auto_save: self._auto_save()
        │   │
        │   ├── [第 91 行] self.add_message(Message("计算结果是 112。具体计算过程是：...", "assistant"))
        │   │   └── 同上
        │   │
        │   └── [第 92 行] return "计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。"
        │
        └──==== 循环结束，返回结果 ====
```

### 阶段 3: 输出结果

```
[第 56 行] print(f"\n🎯 测试1结果: {result1}")
    └── 输出: 🎯 测试1结果: 计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。
```

---

# 测试用例 2: 信息搜索问题

## 输入
```python
search_question = "Python编程语言是什么时候发布的？请告诉我具体的年份。"
```

## 完整调用链

### 阶段 1: 初始化 (复用测试1的agent实例)

使用相同的 agent 实例，工具已注册。

### 阶段 2: 执行测试2 - 搜索问题

```
[第 65 行] result2 = agent.run("Python编程语言是什么时候发布的？请告诉我具体的年份。")
│
└── MyReActAgent.run() [my_react_agent.py 第 60 行]
    │
    │==== 第 1 步 ====
    │
    ├── 构建提示词 (问题: "Python编程语言是什么时候发布的？...")
    │
    ├── 调用 LLM
    │   └── LLM 可能的响应:
    │       ```
    │       Thought: 用户询问 Python 编程语言的发布年份。这需要搜索互联网来获取准确信息。我应该使用 search 工具。
    │       Action: search[Python编程语言发布年份]
    │       ```
    │
    ├── 解析输出
    │   ├── thought = "用户询问 Python 编程语言的发布年份..."
    │   └── action = "search[Python编程语言发布年份]"
    │
    ├── 检查是否完成
    │   └── False (action 不是 Finish)
    │
    ├── 解析工具调用
    │   ├── tool_name = "search"
    │   └── tool_input = "Python编程语言发布年份"
    │
    └── 执行工具
    └── observation = self.tool_registry.execute_tool("search", "Python编程语言发布年份")
        └── execute_tool() [registry.py 第 132-220 行]
            │
            ├── 检查熔断器
            │   └── is_open("search") → False
            │
            ├── 查找 Tool 对象
            │   └── "search" 不在 self._tools 中
            │
            ├── 查找函数工具
            │   └── func = self._functions["search"]["func"]
            │       └── search() [search.py 第 42-82 行]
            │           ├── [第 49-51 行] 检查 SERPAPI_API_KEY
            │           ├── [第 53-59 行] 构建 API 参数
            │           ├── [第 61-62 行] 调用 SerpApiClient
            │           ├── [第 65-77 行] 解析搜索结果
            │           │   ├── 优先返回 answer_box_list
            │           │   │ 或 answer_box.answer
            │           │   │ 或 knowledge_graph.description
            │           │   │ 或 organic_results 前三条
            │           └── 返回搜索结果
            │
            └── 包装为 ToolResponse
                └── text: "Python 编程语言首次发布于 1991 年。由 Guido van Rossum 创建..."

        └── current_history.append("Action: search[Python编程语言发布年份]")
        └── current_history.append("Observation: Python 编程语言首次发布于 1991 年...")

    │==== 第 2 步 ====
    │
    ├── 构建提示词 (包含上一步的历史)
    │
    ├── 调用 LLM
    │   └── LLM 可能的响应:
    │       ```
    │       Thought: 搜索结果显示 Python 首次发布于 1991 年。现在我有足够的信息来回答用户的问题。
    │       Action: Finish[Python 编程语言是在 1991 年发布的。由 Guido van Rossum 创建。]
    │       ```
    │
    ├── 解析输出
    │   ├── thought = "搜索结果显示 Python 首次发布于 1991 年..."
    │   └── action = "Finish[Python 编程语言是在 1991 年发布的...]"
    │
    ├── 检查是否完成
    │   └── True (action 以 Finish 开头)
    │
    ├── 提取答案
    │   └── final_answer = "Python 编程语言是在 1991 年发布的。由 Guido van Rossum 创建。"
    │
    ├── 保存消息到历史
    │   ├── add_message(Message("Python编程语言是什么时候发布的？...", "user"))
    │   └── add_message(Message("Python 编程语言是在 1991 年发布的...", "assistant"))
    │
    └── 返回结果
        └── "Python 编程语言是在 1991 年发布的。由 Guido van Rossum 创建。"
```

### 阶段 3: 输出结果

```
[第 66 行] print(f"\n🎯 测试2结果: {result2}")
    └── 输出: 🎯 测试2结果: Python 编程语言是在 1991 年发布的。由 Guido van Rossum 创建。
```

---

# 测试用例 3: 复合推理问题

## 输入
```python
complex_question = "如果一个班级有30个学生，其中60%是女生，那么男生有多少人？请先计算女生人数，再计算男生人数。"
```

## 完整调用链

### 阶段 1: 初始化 (复用测试1的agent实例)

使用相同的 agent 实例。

### 阶段 2: 执行测试3 - 复合推理

```
[第 75 行] result3 = agent.run("如果一个班级有30个学生，其中60%是女生，那么男生有多少人？请先计算女生人数，再计算男生人数。")
│
└── MyReActAgent.run() [my_react_agent.py 第 60 行]
    │
    │==== 第 1 步：计算女生人数 ====
    │
    ├── 构建提示词 (问题: "如果一个班级有30个学生...")
    │
    ├── 调用 LLM
    │   └── LLM 可能的响应:
    │       ```
    │       Thought: 用户要求我计算班级中女生和男生的人数。首先需要计算女生人数：30 × 60%。
    │       Action: calculate[30 * 0.6]
    │       ```
    │
    ├── 解析输出
    │   ├── thought = "用户要求我计算班级中女生和男生的人数..."
    │   └── action = "calculate[30 * 0.6]"
    │
    ├── 执行工具
    │   └── observation = tool_registry.execute_tool("calculate", "30 * 0.6")
    │       └── 返回: "计算结果: 18.0"
    │
    └── 记录历史
        ├── current_history.append("Action: calculate[30 * 0.6]")
        └── current_history.append("Observation: 计算结果: 18.0")

    │==== 第 2 步：计算男生人数 ====
    │
    ├── 构建提示词 (包含第1步的历史)
    │
    ├── 调用 LLM
    │   └── LLM 可能的响应:
    │       ```
    │       Thought: 女生有 18 人。现在需要计算男生人数：30 - 18 = 12。
    │       Action: calculate[30 - 18]
    │       ```
    │
    ├── 解析输出
    │   └── action = "calculate[30 - 18]"
    │
    ├── 执行工具
    │   └── observation = tool_registry.execute_tool("calculate", "30 - 18")
    │       └── 返回: "计算结果: 12"
    │
    └── 记录历史
        ├── current_history.append("Action: calculate[30 - 18]")
        └── current_history.append("Observation: 计算结果: 12")

    │==== 第 3 步：给出最终答案 ====
    │
    ├── 构建提示词 (包含第1、2步的历史)
    │
    ├── 调用 LLM
    │   └── LLM 可能的响应:
    │       ```
    │       Thought: 我已经计算出女生有 18 人，男生有 12 人。现在可以回答用户的问题了。
    │       Action: Finish[班级中女生有 18 人，男生有 12 人。计算过程：女生人数 = 30 × 60% = 18 人；男生人数 = 30 - 18 = 12 人。]
    │       ```
    │
    ├── 解析输出
    │   └── action = "Finish[班级中女生有 18 人，男生有 12 人...]"
    │
    ├── 检查是否完成
    │   └── True
    │
    ├── 提取答案
    │   └── final_answer = "班级中女生有 18 人，男生有 12 人。计算过程：女生人数 = 30 × 60% = 18 人；男生人数 = 30 - 18 = 12 人。"
    │
    ├── 保存消息到历史
    │   ├── add_message(Message("如果一个班级有30个学生...", "user"))
    │   └── add_message(Message("班级中女生有 18 人，男生有 12 人...", "assistant"))
    │
    └── 返回结果
        └── "班级中女生有 18 人，男生有 12 人。计算过程：女生人数 = 30 × 60% = 18 人；男生人数 = 30 - 18 = 12 人。"
```

### 阶段 3: 输出结果

```
[第 76 行] print(f"\n🎯 测试3结果: {result3}")
    └── 输出: 🎯 测试3结果: 班级中女生有 18 人，男生有 12 人。计算过程：女生人数 = 30 × 60% = 18 人；男生人数 = 30 - 18 = 12 人。
```

---

# 测试用例 4: 自定义提示词测试

## 输入
```python
math_question = "计算 15 × 8 + 32 ÷ 4 的结果"
```

## 完整调用链

### 阶段 1: 初始化 (test_custom_prompt 函数)

```
test_custom_prompt() [第 92 行]
│
├── [第 99 行] llm = HelloAgentsLLM()
│   └── 同测试1
│
├── [第 100 行] tool_registry = ToolRegistry()
│   └── 同测试1
│
├── [第 104-106 行] 注册计算器工具
│   └── tool_registry.register_function(calculate)
│
├── [第 110-121 行] 创建自定义提示词
│   └── custom_prompt =
│       """
│       你是一个数学专家AI助手。
│
│       可用工具：{tools}
│
│       请按以下格式回应：
│       Thought: [你的思考]
│       Action: [tool_name[input] 或 Finish[答案]]
│
│       问题：{question}
│       历史：{history}
│
│       开始：
│       """
│
└── [第 124-130 行] custom_agent = MyReActAgent(
        name="数学专家助手",
        llm=llm,
        tool_registry=tool_registry,
        max_steps=3,
        custom_prompt=custom_prompt
    )
    └── __init__() [my_react_agent.py 第 43-58 行]
        ├── super().__init__(...) (同测试1)
        ├── self.tool_registry = tool_registry
        ├── self.max_steps = 3  # 注意：这里是 3 而不是 5
        ├── self.current_history = []
        └── self.prompt_template = custom_prompt  # 使用自定义提示词
```

### 阶段 2: 执行自定义提示词测试

```
[第 137 行] result = custom_agent.run("计算 15 × 8 + 32 ÷ 4 的结果")
│
└── MyReActAgent.run() [my_react_agent.py 第 60 行]
    │
    │==== 第 1 步 ====
    │
    ├── 构建提示词 (使用自定义模板)
    │   └── prompt = custom_prompt.format(
        tools="calculate: 执行数学计算，支持基本的四则运算",
        question="计算 15 × 8 + 32 ÷ 4 的结果",
        history=""
    )
    │   └── 填充后的提示词:
    │       """
    │       你是一个数学专家AI助手。
    │
    │       可用工具：calculate: 执行数学计算，支持基本的四则运算
    │
    │       请按以下格式回应：
    │       Thought: [你的思考]
    │       Action: [tool_name[input] 或 Finish[答案]]
    │
    │       问题：计算 15 × 8 + 32 ÷ 4 的结果
    │       历史：
    │
    │       开始：
    │       """
    │
    ├── 调用 LLM
    │   └── LLM 可能的响应 (使用自定义提示词，更简洁):
    │       ```
    │       Thought: 需要计算 15 × 8 + 32 ÷ 4
    │       Action: calculate[15 * 8 + 32 / 4]
    │       ```
    │
    ├── 执行工具
    │   └── observation = tool_registry.execute_tool("calculate", "15 * 8 + 32 / 4")
    │       └── 返回: "计算结果: 128.0"
    │
    └── 记录历史
        ├── current_history.append("Action: calculate[15 * 8 + 32 / 4]")
        └── current_history.append("Observation: 计算结果: 128.0")

    │==== 第 2 步 ====
    │
    ├── 构建提示词 (包含历史)
    │
    ├── 调用 LLM
    │   └── LLM 可能的响应:
    │       ```
    │       Thought: 计算结果是 128.0
    │       Action: Finish[15 × 8 + 32 ÷ 4 = 128]
    │       ```
    │
    ├── 检查是否完成
    │   └── True
    │
    ├── 提取答案
    │   └── final_answer = "15 × 8 + 32 ÷ 4 = 128"
    │
    ├── 保存消息到历史
    │   ├── add_message(Message("计算 15 × 8 + 32 ÷ 4 的结果", "user"))
    │   └── add_message(Message("15 × 8 + 32 ÷ 4 = 128", "assistant"))
    │
    └── 返回结果
        └── "15 × 8 + 32 ÷ 4 = 128"
```

### 阶段 3: 输出结果

```
[第 138 行] print(f"\n🎯 自定义提示词测试结果: {result}")
    └── 输出: 🎯 自定义提示词测试结果: 15 × 8 + 32 ÷ 4 = 128
```

---

# 总结：测试用例对比

| 测试用例 | 问题类型 | 工具调用 | 步数 | 特点 |
|---------|---------|---------|------|------|
| 测试1 | 数学计算 | calculate | 2步 | 单次工具调用，直接得出结果 |
| 测试2 | 信息搜索 | search | 2步 | 搜索工具获取外部信息 |
| 测试3 | 复合推理 | calculate × 2 | 3步 | 多步骤推理，需要多次工具调用 |
| 测试4 | 自定义提示词 | calculate | 2步 | 使用自定义提示词模板，max_steps=3 |

---

# 关键调用路径总结

## HelloAgentsLLM 初始化路径

```
HelloAgentsLLM.__init__()
  ├── _auto_detect_provider() → 检测 LLM 提供商
  ├── _resolve_credentials() → 解析 API 密钥
  ├── _get_default_model() → 获取默认模型
  └── _create_client() → 创建 OpenAI 客户端
```

## MyReActAgent 执行路径

```
MyReActAgent.run()
  ├── while current_step < max_steps:
  │   ├── 构建提示词 (工具描述 + 历史 + 问题)
  │   ├── 调用 LLM (llm.invoke)
  │   ├── 解析输出 (提取 Thought 和 Action)
  │   ├── if Action == Finish:
  │   │   ├── 保存消息到历史
  │   │   └── 返回答案
  │   └── else (工具调用):
  │       ├── 解析工具名和参数
  │       ├── 执行工具 (tool_registry.execute_tool)
  │       │   ├── 检查熔断器
  │       │   ├── 查找并执行工具
  │       │   └── 记录熔断器结果
  │       └── 更新历史
  └── 达到最大步数返回超时响应
```

## 工具执行路径

```
tool_registry.execute_tool(name, input)
  ├── 检查熔断器状态
  ├── if name in _tools:
  │   └── tool.run_with_timing(parameters)
  ├── elif name in _functions:
  │   ├── func(input)
  │   └── 包装为 ToolResponse
  └── 记录熔断器结果
```

## 历史管理路径

```
agent.add_message(message)
  ├── history_manager.append(message)
  ├── token_counter.count_message(message) → 增量更新 Token 计数
  ├── if _should_compress():
  │   └── _compress_history()
  └── if auto_save:
      └── _auto_save()
```

---

# 文件依赖关系图

```
demo/test_react_agent.py
    │
    ├── core/llm.py (HelloAgentsLLM)
    │   ├── openai.OpenAI
    │   └── dotenv
    │
    ├── tools/registry.py (ToolRegistry)
    │   ├── tools/base.py (Tool)
    │   ├── tools/response.py (ToolResponse)
    │   ├── tools/circuit_breaker.py (CircuitBreaker)
    │   └── tools/errors.py (ToolErrorCode)
    │
    ├── demo/my_react_agent.py (MyReActAgent)
    │   ├── agents/react_agent.py (ReActAgent)
    │   │   └── core/agent.py (Agent)
    │   │       ├── context/history.py (HistoryManager)
    │   │       ├── context/truncator.py (ObservationTruncator)
    │   │       ├── context/token_counter.py (TokenCounter)
    │   │       ├── core/message.py (Message)
    │   │       └── core/config.py (Config)
    │   └── MY_REACT_PROMPT
    │
    └── tools/builtin/
        ├── calculator.py (calculate)
        │   ├── ast (表达式解析)
        │   ├── operator (数学运算)
        │   └── math (数学函数)
        │
        └── search.py (search)
            └── serpapi (Google 搜索 API)
```

---

# 数据流示意图

```
用户输入
    │
    ▼
┌─────────────────┐
│  MyReActAgent   │
│     .run()      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  构建提示词      │
│  - 工具描述      │
│  - 历史记录      │
│  - 用户问题      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLM.invoke()  │
│  调用大语言模型   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  解析输出        │
│  - Thought      │
│  - Action       │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  Finish   工具调用
    │         │
    │         ▼
    │    ┌─────────────────┐
    │    │ ToolRegistry    │
    │    │ .execute_tool() │
    │    └────────┬────────┘
    │             │
    │             ▼
    │    ┌─────────────────┐
    │    │  执行工具函数     │
    │    │  - calculate    │
    │    │  - search       │
    │    └────────┬────────┘
    │             │
    │             ▼
    │    ┌─────────────────┐
    │    │  包装响应        │
    │    │  ToolResponse   │
    │    └────────┬────────┘
    │             │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────┐
    │  更新历史记录    │
    └────────┬────────┘
             │
             ▼
        继续循环/返回结果
```

---

# 时间线视图

```
T0: test_react_agent() 开始
    ├─ T1: load_dotenv()
    ├─ T2: HelloAgentsLLM 初始化
    ├─ T3: ToolRegistry 初始化
    ├─ T4: 注册 calculate 工具
    ├─ T5: 注册 search 工具
    └─ T6: MyReActAgent 初始化

T10: 测试1 开始
    ├─ T11: 第1步 - 调用 LLM
    ├─ T12: 第1步 - 执行 calculate[(25+15)*3-8]
    ├─ T13: 第2步 - 调用 LLM
    └─ T14: 第2步 - Finish[计算结果是 112...]

T20: 测试2 开始
    ├─ T21: 第1步 - 调用 LLM
    ├─ T22: 第1步 - 执行 search[Python发布年份]
    ├─ T23: 第2步 - 调用 LLM
    └─ T24: 第2步 - Finish[Python发布于1991年...]

T30: 测试3 开始
    ├─ T31: 第1步 - 调用 LLM
    ├─ T32: 第1步 - 执行 calculate[30*0.6]
    ├─ T33: 第2步 - 调用 LLM
    ├─ T34: 第2步 - 执行 calculate[30-18]
    ├─ T35: 第3步 - 调用 LLM
    └─ T36: 第3步 - Finish[女生18人，男生12人...]

T40: test_custom_prompt() 开始
    ├─ T41: 创建新的 LLM 和 ToolRegistry
    ├─ T42: 注册 calculate 工具
    ├─ T43: 创建自定义提示词
    └─ T44: 初始化 custom_agent (max_steps=3)

T50: 自定义提示词测试开始
    ├─ T51: 第1步 - 调用 LLM (使用自定义提示词)
    ├─ T52: 第1步 - 执行 calculate[15*8+32/4]
    ├─ T53: 第2步 - 调用 LLM
    └─ T54: 第2步 - Finish[15×8+32÷4=128]

T99: 所有测试完成
```

---

# 附录：关键代码片段

## MY_REACT_PROMPT 模板

```python
MY_REACT_PROMPT = """你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤：

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一：
- `{{tool_name}}[{{tool_input}}]` - 调用指定工具
- `Finish[最终答案]` - 当你有足够信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循：工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动：
"""
```

## _parse_output 方法

```python
def _parse_output(self, response_text: str):
    """解析LLM输出，提取思考和行动"""
    # 提取 Thought
    thought_match = re.search(r'Thought:\s*(.*?)(?=Action:|$)', response_text, re.DOTALL)
    thought = thought_match.group(1).strip() if thought_match else ""

    # 提取 Action
    action_match = re.search(r'Action:\s*(.*)', response_text, re.DOTALL)
    action = action_match.group(1).strip() if action_match else ""

    return thought, action
```

## _parse_action 方法

```python
def _parse_action(self, action_text: str):
    """解析行动文本，提取工具名称和输入"""
    # 匹配工具调用格式：tool_name[input]
    match = re.match(r'(\w+)\[(.*)\]', action_text)
    if match:
        return match.group(1), match.group(2)
    return None, None
```
