# demo/test_react_agent.py 各测试用例详细完整代码执行调用链

## 文件概述

**文件路径**: `demo/test_react_agent.py`

**测试函数**:
- `test_react_agent()` - 基础功能测试（3个测试用例）
- `test_custom_prompt()` - 自定义提示词测试（1个测试用例）

---

# 测试用例 1: 数学计算问题 - 完整代码执行流程

## 输入
```python
math_question = "请帮我计算：(25 + 15) * 3 - 8 的结果是多少？"
```

## 完整代码执行调用链

### 第一阶段: 初始化阶段 (代码行执行顺序)

```
[SCRIPT START] python demo/test_react_agent.py
│
├── [Line 1-2] 导入语句
│   ├── from dotenv import load_dotenv
│   ├── from tiny_agents.core.llm import HelloAgentsLLM
│   ├── from tiny_agents.tools.registry import ToolRegistry
│   └── from tiny_agents.demo.my_react_agent import MyReActAgent
│
├── [Line 8] load_dotenv()
│   └── [dotenv.py] 执行: 从 .env 文件加载环境变量
│       ├── 读取 .env 文件
│       ├── 解析 key=value 格式
│       └── 设置到 os.environ
│
├── [Line 142-144] if __name__ == "__main__": 条件判断
│   └── 条件: True (主程序执行)
│
├── [Line 144] test_react_agent() 开始执行
│   │
│   ├── [Line 13-14] llm = HelloAgentsLLM()
│   │   └── [core/llm.py:30-74] __init__() 执行流程
│   │       │
│   │   ├── [Line 55] self.model = model or os.getenv("LLM_MODEL_ID")
│   │   │   ├── model 参数 = None (未传入)
│   │   │   ├── os.getenv("LLM_MODEL_ID") → 可能返回 "GLM-4.7" 或其他值
│   │   │   └── self.model = "GLM-4.7" (假设从环境变量获取)
│   │   │
│   │   ├── [Line 56] self.temperature = temperature = 0.7 (默认值)
│   │   ├── [Line 57] self.max_tokens = max_tokens = None (默认值)
│   │   ├── [Line 58] self.timeout = timeout or int(os.getenv("LLM_TIMEOUT", "60"))
│   │   │   └── self.timeout = 60 (默认值)
│   │   ├── [Line 59] self.kwargs = {} (空字典)
│   │   │
│   │   ├── [Line 62] self.provider = provider or self._auto_detect_provider(api_key, base_url)
│   │   │   └── [core/llm.py:76-160] _auto_detect_provider() 执行流程
│   │   │       │
│   │   │   ├── [Line 87-102] 检查特定提供商的环境变量
│   │   │   │   ├── os.getenv("OPENAI_API_KEY") → None
│   │   │   │   ├── os.getenv("DEEPSEEK_API_KEY") → None
│   │   │   │   ├── os.getenv("DASHSCOPE_API_KEY") → None
│   │   │   │   ├── os.getenv("MODELSCOPE_API_KEY") → None
│   │   │   │   ├── os.getenv("KIMI_API_KEY") → None
│   │   │   │   ├── os.getenv("ZHIPU_API_KEY") → "sk-xxxxx" (假设存在)
│   │   │   │   └── 返回 "zhipu"
│   │   │   │
│   │   │   └── [Line 160] return "zhipu"
│   │   │
│   │   ├── [Line 65] self.api_key, self.base_url = self._resolve_credentials(api_key, base_url)
│   │   │   └── [core/llm.py:162-213] _resolve_credentials() 执行流程
│   │   │       │
│   │   │   ├── [Line 189-192] self.provider == "zhipu" → True
│   │   │   │   ├── resolved_api_key = api_key or os.getenv("ZHIPU_API_KEY") or os.getenv("LLM_API_KEY")
│   │   │   │   │   └── resolved_api_key = "sk-xxxxx"
│   │   │   │   ├── resolved_base_url = base_url or os.getenv("LLM_BASE_URL") or "https://open.bigmodel.cn/api/paas/v4"
│   │   │   │   │   └── resolved_base_url = "https://open.bigmodel.cn/api/paas/v4"
│   │   │   │   └── return ("sk-xxxxx", "https://open.bigmodel.cn/api/paas/v4")
│   │   │   │
│   │   │   ├── self.api_key = "sk-xxxxx"
│   │   │   └── self.base_url = "https://open.bigmodel.cn/api/paas/v4"
│   │   │
│   │   ├── [Line 68] if not self.model: 判断
│   │   │   └── self.model = "GLM-4.7" → 非空 → 跳过
│   │   │
│   │   ├── [Line 70-71] if not all([self.api_key, self.base_url]):
│   │   │   ├── all(["sk-xxxxx", "https://..."]) → True
│   │   │   └── 跳过异常抛出
│   │   │
│   │   ├── [Line 74] self._client = self._create_client()
│   │   │   └── [core/llm.py:215-221] _create_client() 执行流程
│   │   │       ├── from openai import OpenAI
│   │   │   └── return OpenAI(
│   │   │           api_key="sk-xxxxx",
│   │   │           base_url="https://open.bigmodel.cn/api/paas/v4",
│   │   │           timeout=60
│   │   │       )
│   │   │       └── 返回 OpenAI 客户端实例
│   │   │
│   │   └── 返回 HelloAgentsLLM 实例
│   │       ├── self.model = "GLM-4.7"
│   │       ├── self.provider = "zhipu"
│   │       ├── self.api_key = "sk-xxxxx"
│   │       ├── self.base_url = "https://open.bigmodel.cn/api/paas/v4"
│   │       └── self._client = OpenAI(...)
│   │
│   ├── [Line 17] tool_registry = ToolRegistry()
│   │   └── [tools/registry.py:20-28] __init__() 执行流程
│   │       ├── [Line 21] self._tools: dict[str, Tool] = {}
│   │       ├── [Line 22] self._functions: dict[str, dict] = {}
│   │       ├── [Line 25] self.read_metadata_cache: Dict = {}
│   │       ├── [Line 28] self.circuit_breaker = circuit_breaker or CircuitBreaker()
│   │       │   └── [tools/circuit_breaker.py:22-44] CircuitBreaker.__init__()
│   │       │   ├── [Line 36] self.failure_threshold = 3
│   │       │   ├── [Line 37] self.recovery_timeout = 300
│   │       │   ├── [Line 38] self.enabled = True
│   │       │   ├── [Line 41] self.failure_counts: Dict[str, int] = defaultdict(int)
│   │       │   └── [Line 44] self.open_timestamps: Dict[str, float] = {}
│   │       │
│   │   └── 返回 ToolRegistry 实例
│   │       ├── self._tools = {}
│   │       ├── self._functions = {}
│   │       ├── self.read_metadata_cache = {}
│   │       └── self.circuit_breaker = CircuitBreaker(...)
│   │
│   ├── [Line 20] print("🔧 注册测试工具...")
│   │   └── 输出: 🔧 注册测试工具...
│   │
│   ├── [Line 24-25] from tiny_agents.tools.builtin.calculator import calculate
│   │   └── [tools/builtin/calculator.py] 执行导入
│   │       └── 函数 calculate 定义在 Line 145-156
│   │
│   ├── [Line 25] tool_registry.register_function("calculate", "执行数学计算，支持基本的四则运算", calculate)
│   │   └── [tools/registry.py:57-110] register_function() 执行流程
│   │       │
│   │   ├── [Line 84-87] 兼容旧调用方式检查
│   │   │   ├── isinstance(func, str) → False (func 是函数对象)
│   │   │   └── 跳过旧方式兼容逻辑
│   │   │
│   │   ├── [Line 89-91] 自动提取名称
│   │   │   ├── if name is None: → False (name = "calculate")
│   │   │   └── 跳过，使用传入的 name
│   │   │
│   │   ├── [Line 93-101] 自动提取描述
│   │   │   ├── if description is None: → False
│   │   │   └── 跳过，使用传入的 description
│   │   │
│   │   ├── [Line 103-104] if name in self._functions:
│   │   │   ├── "calculate" in {} → False
│   │   │   └── 跳过警告
│   │   │
│   │   ├── [Line 106-110] 注册函数
│   │   │   ├── self._functions["calculate"] = {
│   │   │   │   "description": "执行数学计算，支持基本的四则运算",
│   │   │   │   "func": calculate
│   │   │   │   }
│   │   │   └── [Line 110] print(f"✅ 函数工具 'calculate' 已注册。")
│   │   │       └── 输出: ✅ 函数工具 'calculate' 已注册。
│   │   │
│   │   └── 返回 None
│   │
│   ├── [Line 26] print("✅ 计算器工具注册成功")
│   │   └── 输出: ✅ 计算器工具注册成功
│   │
│   ├── [Line 32-33] from tiny_agents.tools.builtin.search import search
│   │   └── [tools/builtin/search.py] 执行导入
│   │   └── 函数 search 定义在 Line 42-82
│   │
│   ├── [Line 33] tool_registry.register_function("search", "搜索互联网信息", search)
│   │   └── [tools/registry.py:57-110] register_function() 执行流程
│   │       │
│   │   ├── ... (类似 calculate 注册流程)
│   │   │
│   │   ├── [Line 106-110] 注册函数
│   │   │   ├── self._functions["search"] = {
│   │   │   │   "description": "搜索互联网信息",
│   │   │   │   "func": search
│   │   │   │   }
│   │   │   └── [Line 110] print(f"✅ 函数工具 'search' 已注册。")
│   │   │       └── 输出: ✅ 函数工具 'search' 已注册。
│   │   │
│   │   └── 返回 None
│   │
│   ├── [Line 34] print("✅ 搜索工具注册成功")
│   │   └── 输出: ✅ 搜索工具注册成功
│   │
│   ├── [Line 39-44] agent = MyReActAgent(...)
│   │   └── [demo/my_react_agent.py:43-58] MyReActAgent.__init__() 执行流程
│   │       │
│   │   ├── [Line 53] super().__init__(name, llm, system_prompt, config)
│   │   │   └── [agents/react_agent.py:52-80] ReActAgent.__init__()
│   │   │       └── [Line 74] super().__init__(name, llm, system_prompt, config)
│   │   │           └── [core/agent.py:32-131] Agent.__init__() 执行流程
│   │   │               │
│   │   │           ├── [Line 40-42] 初始化基础属性
│   │   │           │   ├── self.name = "我的推理行动助手"
│   │   │           │   ├── self.llm = llm (HelloAgentsLLM 实例)
│   │   │           │   └── self.system_prompt = None
│   │   │           │
│   │   │           ├── [Line 43] self.config = config or Config()
│   │   │           │   └── [core/config.py] Config() 实例化
│   │   │           │       ├── context_window: int = 8192
│   │   │           │       ├── compression_threshold: float = 0.8
│   │   │           │       ├── min_retain_rounds: int = 2
│   │   │           │       ├── tool_output_max_lines: int = 100
│   │   │           │       ├── tool_output_max_bytes: int = 10000
│   │   │           │       ├── tool_output_truncate_direction: str = "end"
│   │   │           │       ├── ... (其他配置项)
│   │   │           │       └── 返回 Config 实例
│   │   │           │
│   │   │           ├── [Line 45-46] self.tool_registry = tool_registry
│   │   │           │   └── self.tool_registry = tool_registry (ToolRegistry 实例)
│   │   │           │
│   │   │           ├── [Line 49-55] 初始化 HistoryManager
│   │   │           │   └── [context/history.py] HistoryManager() 实例化
│   │   │           │       ├── min_retain_rounds: int = 2
│   │   │           │       ├── compression_threshold: float = 0.8
│   │   │           │       └── 返回 HistoryManager 实例
│   │   │           │
│   │   │           ├── [Line 57-62] 初始化 ObservationTruncator
│   │   │           │   └── [context/truncator.py] ObservationTruncator() 实例化
│   │   │           │       ├── max_lines: int = 100
│   │   │           │       ├── max_bytes: int = 10000
│   │   │           │       ├── truncate_direction: str = "end"
│   │   │           │       └── 返回 ObservationTruncator 实例
│   │   │           │
│   │   │           ├── [Line 64-66] 初始化 TokenCounter
│   │   │           │   └── [context/token_counter.py] TokenCounter() 实例化
│   │   │           │       ├── model: str = "GLM-4.7"
│   │   │           │       └── 返回 TokenCounter 实例
│   │   │           │
│   │   │           ├── [Line 69-87] 初始化 TraceLogger (如果 config.trace_enabled)
│   │   │           │   ├── if self.config.trace_enabled: → False (默认关闭)
│   │   │           │   └── 跳过
│   │   │           │
│   │   │           ├── [Line 90-102] 初始化 SkillLoader (如果 config.skills_enabled)
│   │   │           │   ├── if self.config.skills_enabled: → False (默认关闭)
│   │   │           │   └── 跳过
│   │   │           │
│   │   │           ├── [Line 105-131] 初始化 SessionStore (如果 config.session_enabled)
│   │   │           │   ├── if self.config.session_enabled: → False (默认关闭)
│   │   │           │   └── 跳过
│   │   │           │
│   │   │           └── 返回 Agent 基类实例化完成
│   │   │
│   │   ├── [Line 75-76] self.tool_registry = tool_registry
│   │   │   └── self.tool_registry = tool_registry (覆盖基类属性)
│   │   │
│   │   ├── [Line 76] self.max_steps = max_steps = 5
│   │   │   └── self.max_steps = 5
│   │   │
│   │   ├── [Line 77] self.current_history: List[str] = []
│   │   │   └── self.current_history = []
│   │   │
│   │   ├── [Line 78] self.prompt_template = custom_prompt if custom_prompt else MY_REACT_PROMPT
│   │   │   ├── custom_prompt = None (未传入)
│   │   │   └── self.prompt_template = MY_REACT_PROMPT (模块级常量)
│   │   │
│   │   ├── [Line 79] print(f"✅ {name} 初始化完成，最大步数: {max_steps}")
│   │   │   └── 输出: ✅ 我的推理行动助手 初始化完成，最大步数: 5
│   │   │
│   │   └── 返回 MyReActAgent 实例
│   │
│   ├── [Line 46-48] print("="*60)
│   │   └── 输出: ============================================================
│   │
│   ├── [Line 48] print("开始测试 MyReActAgent")
│   │   └── 输出: 开始测试 MyReActAgent
│   │
│   ├── [Line 49] print("="*60)
│   │   └── 输出: ============================================================
│   │
│   └── 初始化阶段完成
```

### 第二阶段: 执行测试1 - 数学计算

```
├── [Line 51-52] print("\n📊 测试1：数学计算问题")
│   └── 输出: (换行)📊 测试1：数学计算问题
│
├── [Line 52] math_question = "请帮我计算：(25 + 15) * 3 - 8 的结果是多少？"
│   └── math_question = "请帮我计算：(25 + 15) * 3 - 8 的结果是多少？"
│
├── [Line 54-58] try: 开始异常捕获
│   │
│   ├── [Line 55] result1 = agent.run(math_question)
│   │   └── [demo/my_react_agent.py:60-105] MyReActAgent.run() 执行流程
│   │       │
│   │   ├── [Line 62] self.current_history = []
│   │   │   └── self.current_history = [] (清空历史)
│   │   │
│   │   ├── [Line 63] current_step = 0
│   │   │   └── current_step = 0
│   │   │
│   │   ├── [Line 65] print(f"\n🤖 {self.name} 开始处理问题: {input_text}")
│   │   │   └── 输出: (换行)🤖 我的推理行动助手 开始处理问题: 请帮我计算：(25 + 15) * 3 - 8 的结果是多少？
│   │   │
│   │   └── [Line 67] while current_step < self.max_steps:
│   │       └── while 0 < 5: → True，进入循环
│   │           │
│   │           │========= 第 1 步开始 =========
│   │           │
│   │           ├── [Line 68] current_step += 1
│   │           │   └── current_step = 1
│   │           │
│   │           ├── [Line 69] print(f"\n--- 第 {current_step} 步 ---")
│   │           │   └── 输出: (换行)--- 第 1 步 ---
│   │           │
│   │           │--- 构建提示词 ---
│   │           │
│   │           ├── [Line 72] tools_desc = self.tool_registry.get_tools_description()
│   │           │   └── [tools/registry.py:222-239] get_tools_description() 执行流程
│   │           │       │
│   │           │       ├── [Line 225] descriptions = []
│   │           │       │   └── descriptions = []
│   │           │       │
│   │           │       ├── [Line 229-233] 遍历 Tool 对象
│   │           │       │   ├── for tool in self._tools.values():
│   │           │       │   │   └── self._tools = {} → 空迭代，跳过
│   │           │       │
│   │           │       ├── [Line 236-237] 遍历函数工具
│   │           │       │   ├── for name, info in self._functions.items():
│   │           │       │   │
│   │           │       │   ├── 第1次迭代: name="calculate", info={...}
│   │           │       │   │   ├── descriptions.append(f"- {name}: {info['description']}")
│   │           │       │   │   │   └── descriptions = ["- calculate: 执行数学计算，支持基本的四则运算"]
│   │           │       │   │
│   │           │       │   ├── 第2次迭代: name="search", info={...}
│   │           │       │   │   ├── descriptions.append(f"- {name}: {info['description']}")
│   │           │       │   │   │   └── descriptions = [
│   │           │       │   │   │       "- calculate: 执行数学计算，支持基本的四则运算",
│   │           │       │   │   │       "- search: 搜索互联网信息"
│   │           │       │   │   │      ]
│   │           │       │   │
│   │           │       │   └── 迭代结束
│   │           │       │
│   │           │       ├── [Line 239] return "\n".join(descriptions) if descriptions else "暂无可用工具"
│   │           │       │   └── return "- calculate: 执行数学计算，支持基本的四则运算\n- search: 搜索互联网信息"
│   │           │       │
│   │           │       └── tools_desc = "- calculate: 执行数学计算，支持基本的四则运算\n- search: 搜索互联网信息"
│   │           │
│   │           ├── [Line 73] history_str = "\n".join(self.current_history)
│   │           │   └── history_str = "" (current_history 为空)
│   │           │
│   │           ├── [Line 74-78] prompt = self.prompt_template.format(...)
│   │           │   └── 填充 MY_REACT_PROMPT 模板
│   │           │       ├── {tools} → tools_desc
│   │           │       ├── {question} → input_text
│   │           │       └── {history} → history_str
│   │           │
│   │           │   └── prompt =
│   │           │       """
│   │           │       你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。
│   │           │
│   │           │       ## 可用工具
│   │           │       - calculate: 执行数学计算，支持基本的四则运算
│   │           │       - search: 搜索互联网信息
│   │           │
│   │           │       ## 工作流程
│   │           │       请严格按照以下格式进行回应，每次只能执行一个步骤：
│   │           │
│   │           │       Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
│   │           │       Action: 你决定采取的行动，必须是以下格式之一：
│   │           │       - `{{tool_name}}[{{tool_input}}]` - 调用指定工具
│   │           │       - `Finish[最终答案]` - 当你有足够信息给出最终答案时
│   │           │
│   │           │       ## 当前任务
│   │           │       **Question:** 请帮我计算：(25 + 15) * 3 - 8 的结果是多少？
│   │           │
│   │           │       ## 执行历史
│   │           │
│   │           │       现在开始你的推理和行动：
│   │           │       """
│   │           │
│   │           │--- 调用 LLM ---
│   │           │
│   │           ├── [Line 81] messages = [{"role": "user", "content": prompt}]
│   │           │   └── messages = [{"role": "user", "content": "..."}]
│   │           │
│   │           ├── [Line 82] response_text = self.llm.invoke(messages, **kwargs)
│   │           │   └── [core/llm.py:301-316] invoke() 执行流程
│   │           │       │
│   │           │       ├── [Line 307-313] response = self._client.chat.completions.create(
│   │           │       │   ├── model=self.model → "GLM-4.7"
│   │           │       │   ├── messages=messages
│   │           │       │   ├── temperature=kwargs.get('temperature', self.temperature) → 0.7
│   │           │       │   ├── max_tokens=kwargs.get('max_tokens', self.max_tokens) → None
│   │           │       │   └── **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']} → {}
│   │           │       │
│   │           │       │   └── [OpenAI API] HTTP POST 请求
│   │           │       │       ├── URL: https://open.bigmodel.cn/api/paas/v4/chat/completions
│   │           │       │       ├── Headers:
│   │           │       │       │   ├── Authorization: Bearer sk-xxxxx
│   │           │       │       │   └── Content-Type: application/json
│   │           │       │       ├── Body:
│   │           │       │       │   {
│   │           │       │       │     "model": "GLM-4.7",
│   │           │       │       │     "messages": [{"role": "user", "content": "..."}],
│   │           │       │       │     "temperature": 0.7,
│   │           │       │       │     "stream": False
│   │           │       │       │   }
│   │           │       │       └── 等待 API 响应...
│   │           │       │
│   │           │       │   └── 返回 ChatCompletion 对象
│   │           │       │
│   │           │       ├── [Line 314] return response.choices[0].message.content
│   │           │       │
│   │           │       └── response_text = (LLM 生成的响应)
│   │           │           示例响应:
│   │           │           """
│   │           │           Thought: 用户要求计算一个数学表达式 (25 + 15) * 3 - 8。我需要使用计算器工具来计算这个表达式。
│   │           │           Action: calculate[(25 + 15) * 3 - 8]
│   │           │           """
│   │           │
│   │           │--- 解析输出 ---
│   │           │
│   │           ├── [Line 85] thought, action = self._parse_output(response_text)
│   │           │   └── [demo/my_react_agent.py:107-125] _parse_output() 执行流程
│   │           │       │
│   │           │       ├── [Line 118] thought_match = re.search(r'Thought:\s*(.*?)(?=Action:|$)', response_text, re.DOTALL)
│   │           │       │   └── 正则匹配 "Thought:" 后的内容
│   │           │       │       └── thought_match = Match对象
│   │           │       │
│   │           │       ├── [Line 119] thought = thought_match.group(1).strip() if thought_match else ""
│   │           │       │   └── thought = "用户要求计算一个数学表达式 (25 + 15) * 3 - 8。我需要使用计算器工具来计算这个表达式。"
│   │           │       │
│   │           │       ├── [Line 122] action_match = re.search(r'Action:\s*(.*)', response_text, re.DOTALL)
│   │           │       │   └── 正则匹配 "Action:" 后的内容
│   │           │       │       └── action_match = Match对象
│   │           │       │
│   │           │       ├── [Line 123] action = action_match.group(1).strip() if action_match else ""
│   │           │       │   └── action = "calculate[(25 + 15) * 3 - 8]"
│   │           │       │
│   │           │       └── [Line 125] return thought, action
│   │           │           └── 返回 (thought, action)
│   │           │
│   │           ├── thought = "用户要求计算一个数学表达式..."
│   │           ├── action = "calculate[(25 + 15) * 3 - 8]"
│   │           │
│   │           │--- 检查是否完成 ---
│   │           │
│   │           ├── [Line 88] if action and action.startswith("Finish"):
│   │           │   ├── action → "calculate[(25 + 15) * 3 - 8]"
│   │           │   ├── action.startswith("Finish") → False
│   │           │   └── 条件为 False，跳过 Finish 分支
│   │           │
│   │           │--- 执行工具调用 ---
│   │           │
│   │           ├── [Line 95] if action:
│   │           │   └── if "calculate[(25 + 15) * 3 - 8]": → True
│   │           │
│   │           ├── [Line 96] tool_name, tool_input = self._parse_action(action)
│   │           │   └── [demo/my_react_agent.py:127-141] _parse_action() 执行流程
│   │           │       │
│   │           │       ├── [Line 138] match = re.match(r'(\w+)\[(.*)\]', action_text)
│   │           │       │   └── 正则匹配 "工具名[参数]" 格式
│   │           │       │   └── match = Match对象
│   │           │       │       ├── group(1) = "calculate"
│   │           │       │       └── group(2) = "(25 + 15) * 3 - 8"
│   │           │       │
│   │           │       ├── [Line 139-140] if match:
│   │           │       │   └── return match.group(1), match.group(2)
│   │           │       │
│   │           │       └── 返回 ("calculate", "(25 + 15) * 3 - 8")
│   │           │
│   │           ├── tool_name = "calculate"
│   │           ├── tool_input = "(25 + 15) * 3 - 8"
│   │           │
│   │           ├── [Line 97] observation = self.tool_registry.execute_tool(tool_name, tool_input)
│   │           │   └── [tools/registry.py:132-220] execute_tool() 执行流程
│   │           │       │
│   │           │       │--- 检查熔断器 ---
│   │           │       │
│   │           │       ├── [Line 144] if self.circuit_breaker.is_open(name):
│   │           │       │   └── [tools/circuit_breaker.py:46-71] is_open() 执行流程
│   │           │       │       │
│   │           │       │       ├── [Line 57] if not self.enabled:
│   │           │       │       │   └── self.enabled = True → 跳过
│   │           │       │       │
│   │           │       │       ├── [Line 61] if tool_name not in self.open_timestamps:
│   │           │       │       │   ├── "calculate" not in {} → True
│   │           │       │       │   └── [Line 62] return False
│   │           │       │       │
│   │           │       │       └── 返回 False (熔断器关闭)
│   │           │       │
│   │           │       ├── [Line 144] 条件为 False，跳过熔断器错误返回
│   │           │       │
│   │           │       │--- 查找工具 ---
│   │           │       │
│   │           │       ├── [Line 159-182] if name in self._tools:
│   │           │       │   ├── "calculate" in {} → False
│   │           │       │   └── 跳过 Tool 对象查找
│   │           │       │
│   │           │       ├── [Line 185] elif name in self._functions:
│   │           │       │   ├── "calculate" in {"calculate": {...}, "search": {...}} → True
│   │           │       │
│   │           │       │   ├── [Line 186] func = self._functions[name]["func"]
│   │           │       │   │   └── func = calculate 函数 (calculator.py:145-156)
│   │           │       │   │
│   │           │       │   ├── [Line 187] start_time = time.time()
│   │           │       │   │   └── start_time = 1234567890.123 (示例时间戳)
│   │           │       │   │
│   │           │       │   │--- 执行工具函数 ---
│   │           │       │   │
│   │           │       │   ├── [Line 190] result = func(input_text)
│   │           │       │   │   └── [tools/builtin/calculator.py:145-156] calculate() 执行流程
│   │           │       │   │       │
│   │           │       │   │       ├── [Line 155] tool = CalculatorTool()
│   │           │       │   │       │   └── [calculator.py:43-47] CalculatorTool.__init__()
│   │           │       │   │       │       ├── [Line 45] super().__init__(
│   │           │       │   │       │       │   ├──     name="python_calculator",
│   │           │       │   │       │       │   │     description="执行数学计算。支持基本运算、数学函数等。",
│   │           │       │   │       │       │   │     expandable=False
│   │           │       │   │       │       │   │ )
│   │           │       │   │       │       │   │   └── [base.py:67-77] Tool.__init__()
│   │           │       │   │       │       │   │       ├── self.name = "python_calculator"
│   │           │       │   │       │       │   │       ├── self.description = "执行数学计算..."
│   │           │       │   │       │       │   │       └── self.expandable = False
│   │           │       │   │       │       │   │
│   │           │       │   │       │       │   └── 返回 CalculatorTool 实例
│   │           │       │   │       │       │
│   │           │       │   │       │   ├── [Line 156] return tool.run({"input": expression})
│   │           │       │   │       │   │   └── [calculator.py:49-102] run() 执行流程
│   │           │       │   │       │   │       │
│   │           │       │   │       │   │       ├── [Line 60] expression = parameters.get("input", "") or parameters.get("expression", "")
│   │           │       │   │       │   │       │   ├── parameters = {"input": "(25 + 15) * 3 - 8"}
│   │           │       │   │       │   │       │   └── expression = "(25 + 15) * 3 - 8"
│   │           │       │   │       │   │       │
│   │           │       │   │       │   │       ├── [Line 62-66] if not expression:
│   │           │       │   │       │   │       │   └── 非空，跳过错误返回
│   │           │       │   │       │   │       │
│   │           │       │   │       │   │       ├── [Line 68] print(f"🧮 正在计算: {expression}")
│   │           │       │   │       │   │       │   └── 输出: 🧮 正在计算: (25 + 15) * 3 - 8
│   │           │       │   │       │   │       │
│   │           │       │   │       │   │       │--- 解析并计算表达式 ---
│   │           │       │   │       │   │       │
│   │           │       │   │       │   │       ├── [Line 70-73] try:
│   │           │       │   │       │   │       │
│   │           │       │   │       │   │       │   ├── [Line 72] node = ast.parse(expression, mode='eval')
│   │           │       │   │       │   │       │   │   └── 解析表达式为 AST
│   │           │       │   │       │   │       │   │   │   └── Module(body=[Expr(value=BinOp(...))])
│   │           │       │   │       │   │       │   │
│   │           │       │   │       │   │       │   ├── [Line 73] result = self._eval_node(node.body)
│   │           │       │   │       │   │       │   │   └── [calculator.py:104-130] _eval_node() 执行流程
│   │           │       │   │       │   │       │   │       │
│   │           │       │   │       │   │       │   │       ├── 递归计算 AST 节点
│   │           │       │   │       │   │       │   │       │
│   │           │       │   │       │   │       │   │       ├── 节点1: BinOp(left=Constant(25), op=Add, right=Constant(15))
│   │           │       │   │       │   │       │   │       │   ├── operator.add(25, 15) = 40
│   │           │       │   │       │   │       │   │       │   └── 返回 40
│   │           │       │   │       │   │       │   │       │
│   │           │       │   │       │   │       │   │       ├── 节点2: BinOp(left=40, op=Mult, right=Constant(3))
│   │           │       │   │       │   │       │   │       │   ├── operator.mul(40, 3) = 120
│   │           │       │   │       │   │       │   │       │   └── 返回 120
│   │           │       │   │       │   │       │   │       │
│   │           │       │   │       │   │       │   │       ├── 节点3: BinOp(left=120, op=Sub, right=Constant(8))
│   │           │       │   │       │   │       │   │       │   ├── operator.sub(120, 8) = 112
│   │           │       │   │       │   │       │   │       │   └── 返回 112
│   │           │       │   │       │   │       │   │       │
│   │           │       │   │       │   │       │   │       └── 返回 112
│   │           │       │   │       │   │       │   │
│   │           │       │   │       │   │       │   ├── result = 112
│   │           │       │   │       │   │       │
│   │           │       │   │       │   │       │   ├── [Line 74] result_str = str(result)
│   │           │       │   │       │   │       │   │   └── result_str = "112"
│   │           │       │   │       │   │       │   │
│   │           │       │   │       │   │       │   ├── [Line 76] print(f"✅ 计算结果: {result_str}")
│   │           │       │   │       │   │       │   │   └── 输出: ✅ 计算结果: 112
│   │           │       │   │       │   │       │   │
│   │           │       │   │       │   │       │   │--- 创建成功响应 ---
│   │           │       │   │       │   │       │   │
│   │           │       │   │       │   │       │   ├── [Line 78-86] return ToolResponse.success(...)
│   │           │       │   │       │   │       │   │   └── [response.py:93-114] success() 执行流程
│   │           │       │   │       │   │       │   │       ├── [Line 109] status=ToolStatus.SUCCESS
│   │           │       │   │       │   │       │   │       ├── [Line 110] text="计算结果: 112"
│   │           │       │   │       │   │       │   │       ├── [Line 111] data={
│   │           │       │   │       │   │       │   │       │     "expression": "(25 + 15) * 3 - 8",
│   │           │       │   │       │   │       │   │       │     "result": 112,
│   │           │       │   │       │   │       │   │       │     "result_str": "112",
│   │           │       │   │       │   │       │   │       │     "result_type": "int"
│   │           │       │   │       │   │       │   │       │   }
│   │           │       │   │       │   │       │   │       └── 返回 ToolResponse 实例
│   │           │       │   │       │   │       │   │           ├── status = ToolStatus.SUCCESS
│   │           │       │   │       │   │       │   │           ├── text = "计算结果: 112"
│   │           │       │   │       │   │       │   │           ├── data = {...}
│   │           │       │   │       │   │       │   │           └── error_info = None
│   │           │       │   │       │   │       │   │
│   │           │       │   │       │   │       │   └── 返回 ToolResponse 实例
│   │           │       │   │       │   │       │
│   │           │       │   │       │   │       ├── [Line 87-94] except SyntaxError as e:
│   │           │       │   │       │   │       │   └── 无异常，跳过
│   │           │       │   │       │   │       │
│   │           │       │   │       │   │       ├── [Line 95-101] except Exception as e:
│   │           │       │   │       │   │       │   └── 无异常，跳过
│   │           │       │   │       │   │       │
│   │           │       │   │       │   │       └── 返回 ToolResponse 对象
│   │           │       │   │       │   │
│   │           │       │   │       │   └── 返回 ToolResponse 对象
│   │           │       │   │       │
│   │           │       │   │       └── result = ToolResponse 对象
│   │           │       │   │
│   │           │       │   ├── [Line 191] elapsed_ms = int((time.time() - start_time) * 1000)
│   │           │       │   │   ├── time.time() - start_time ≈ 0.002 秒
│   │           │       │   │   └── elapsed_ms = 2
│   │           │       │   │
│   │           │       │   │--- 包装为 ToolResponse ---
│   │           │       │   │
│   │           │       │   ├── [Line 194-199] response = ToolResponse.success(...)
│   │           │       │   │   └── [response.py:93-114] success() 执行流程
│   │           │       │   │       ├── text=str(result)
│   │           │       │   │       │   └── text = "计算结果: 112"
│   │           │       │   │       ├── data={"output": result}
│   │           │       │   │       │   └── data = {"output": ToolResponse(...)}
│   │           │       │   │       ├── stats={"time_ms": elapsed_ms}
│   │           │       │   │       │   └── stats = {"time_ms": 2}
│   │           │       │   │       ├── context={"tool_name": name, "input": input_text}
│   │           │       │   │       │   └── context = {"tool_name": "calculate", "input": "(25 + 15) * 3 - 8"}
│   │           │       │   │       └── 返回 ToolResponse 对象
│   │           │       │   │           ├── status = ToolStatus.SUCCESS
│   │           │       │   │           ├── text = "计算结果: 112"
│   │           │       │   │           ├── data = {"output": ToolResponse(...)}
│   │           │       │   │           ├── stats = {"time_ms": 2}
│   │           │       │   │           └── context = {"tool_name": "calculate", "input": "(25 + 15) * 3 - 8"}
│   │           │       │   │
│   │           │       │   ├── [Line 200-207] except Exception as e:
│   │           │       │   │   └── 无异常，跳过
│   │           │       │   │
│   │           │       │   │--- 记录熔断器结果 ---
│   │           │       │   │
│   │           │       │   ├── [Line 218] self.circuit_breaker.record_result(name, response)
│   │           │       │   │   └── [circuit_breaker.py:73-90] record_result() 执行流程
│   │           │       │   │       │
│   │           │       │   │       ├── [Line 81] if not self.enabled:
│   │           │       │   │       │   └── self.enabled = True → 跳过
│   │           │       │   │       │
│   │           │       │   │       ├── [Line 85] is_error = response.status == ToolStatus.ERROR
│   │           │       │   │       │   ├── response.status = ToolStatus.SUCCESS
│   │           │       │   │       │   └── is_error = False
│   │           │       │   │       │
│   │           │       │   │       ├── [Line 87-90] if is_error:
│   │           │       │   │       │   └── False → 跳过失败处理
│   │           │       │   │       │
│   │           │       │   │       ├── [Line 89] else: self._on_success(tool_name)
│   │           │       │   │       │   └── [circuit_breaker.py:102-105] _on_success() 执行流程
│   │           │       │   │       │       ├── [Line 105] self.failure_counts[tool_name] = 0
│   │           │       │   │       │       │   └── self.failure_counts["calculate"] = 0
│   │           │       │   │       │       │
│   │           │       │   │       │       └── 返回 None
│   │           │       │   │       │
│   │           │       │   │       └── 返回 None
│   │           │       │   │
│   │           │       │   └── [Line 220] return response
│   │           │       │       └── 返回 ToolResponse 对象
│   │           │       │
│   │           │       └── observation = ToolResponse 对象
│   │           │           ├── status = ToolStatus.SUCCESS
│   │           │           ├── text = "计算结果: 112"
│   │           │           └── ...
│   │           │
│   │           │--- 记录历史 ---
│   │           │
│   │           ├── [Line 98] self.current_history.append(f"Action: {action}")
│   │           │   └── self.current_history = ["Action: calculate[(25 + 15) * 3 - 8]"]
│   │           │
│   │           ├── [Line 99] self.current_history.append(f"Observation: {observation}")
│   │           │   └── self.current_history = [
│   │           │       "Action: calculate[(25 + 15) * 3 - 8]",
│   │           │       "Observation: ToolResponse(status=SUCCESS, text='计算结果: 112', ...)"
│   │           │      ]
│   │           │
│   │           └── 继续循环 (回到 Line 67)
│   │
│   │           │========= 第 2 步开始 =========
│   │           │
│   │           ├── [Line 68] current_step += 1
│   │           │   └── current_step = 2
│   │           │
│   │           ├── [Line 69] print(f"\n--- 第 {current_step} 步 ---")
│   │           │   └── 输出: (换行)--- 第 2 步 ---
│   │           │
│   │           │--- 构建提示词 (包含历史) ---
│   │           │
│   │           ├── [Line 72] tools_desc = self.tool_registry.get_tools_description()
│   │           │   └── tools_desc = "- calculate: 执行数学计算，支持基本的四则运算\n- search: 搜索互联网信息"
│   │           │
│   │           ├── [Line 73] history_str = "\n".join(self.current_history)
│   │           │   └── history_str =
│   │           │       """
│   │           │       Action: calculate[(25 + 15) * 3 - 8]
│   │           │       Observation: 计算结果: 112
│   │           │       """
│   │           │
│   │           ├── [Line 74-78] prompt = self.prompt_template.format(...)
│   │           │   └── 填充 MY_REACT_PROMPT 模板 (包含历史)
│   │           │
│   │           │--- 调用 LLM ---
│   │           │
│   │           ├── [Line 81-82] response_text = self.llm.invoke(messages)
│   │           │   └── LLM 可能的响应:
│   │           │       """
│   │           │       Thought: 计算器已经返回了结果，(25 + 15) * 3 - 8 = 112。现在我有足够的信息来回答用户的问题。
│   │           │       Action: Finish[计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。]
│   │           │       """
│   │           │
│   │           │--- 解析输出 ---
│   │           │
│   │           ├── [Line 85] thought, action = self._parse_output(response_text)
│   │           │   ├── thought = "计算器已经返回了结果..."
│   │           │   └── action = "Finish[计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。]"
│   │           │
│   │           │--- 检查是否完成 ---
│   │           │
│   │           ├── [Line 88] if action and action.startswith("Finish"):
│   │           │   ├── action → "Finish[...]"
│   │           │   ├── action.startswith("Finish") → True
│   │           │   └── 条件为 True，进入 Finish 分支
│   │           │
│   │           │   ├── [Line 89] final_answer = self._parse_action_input(action)
│   │           │   │   └── [demo/my_react_agent.py:143-154] _parse_action_input() 执行流程
│   │           │   │       ├── [Line 153] match = re.match(r'\w+\[(.*)\]', action_text)
│   │           │   │   │   └── 正则匹配 "Finish[...]" 格式
│   │           │   │   │       └── match = Match对象
│   │           │   │   │           └── group(1) = "计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。"
│   │           │   │       │
│   │           │   │       ├── [Line 154] return match.group(1) if match else ""
│   │           │   │   │   └── 返回 "计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。"
│   │           │   │       │
│   │           │   │   └── final_answer = "计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。"
│   │           │   │
│   │           │   │--- 保存消息到历史 ---
│   │           │   │
│   │           │   ├── [Line 90] self.add_message(Message(input_text, "user"))
│   │           │   │   └── [core/agent.py:300-320] add_message() 执行流程
│   │           │   │       ├── [Line 305] self.history_manager.append(message)
│   │           │   │       │   └── [context/history.py] append() 执行
│   │           │   │       │       └── 将消息添加到历史管理器
│   │           │   │       │
│   │           │   │       ├── [Line 308] self._history_token_count += self.token_counter.count_message(message)
│   │           │   │       │   └── [context/token_counter.py] count_message() 执行
│   │           │   │       │       └── 计算消息的 Token 数量
│   │           │   │       │
│   │           │   │       ├── [Line 312-313] if self._should_compress():
│   │           │   │       │   └── Token 数量未达到阈值 → False，跳过压缩
│   │           │   │       │
│   │           │   │       ├── [Line 316-319] if auto_save:
│   │           │   │       │   └── auto_save 未启用 → 跳过
│   │           │   │       │
│   │           │   │       └── 返回 None
│   │           │   │
│   │           │   ├── [Line 91] self.add_message(Message(final_answer, "assistant"))
│   │           │   │   └── 同上 (添加助手消息到历史)
│   │           │   │
│   │           │   ├── [Line 92] return final_answer
│   │           │   │   └── 返回 "计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。"
│   │           │   │
│   │           │   └──==== 循环结束，返回结果 ====
│   │           │
│   └── result1 = "计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。"
│
├── [Line 56] print(f"\n🎯 测试1结果: {result1}")
│   └── 输出: (换行)🎯 测试1结果: 计算结果是 112。具体计算过程是：(25 + 15) = 40，然后 40 × 3 = 120，最后 120 - 8 = 112。
│
├── [Line 57-58] except Exception as e:
│   └── 无异常，跳过
│
└── 测试1完成
```

---

# 测试用例 2: 信息搜索问题 - 代码执行流程

## 输入
```python
search_question = "Python编程语言是什么时候发布的？请告诉我具体的年份。"
```

## 代码执行流程 (简化版)

```
[Line 61-62] print("\n🔍 测试2：信息搜索问题")
    └── 输出: (换行)🔍 测试2：信息搜索问题

[Line 62] search_question = "Python编程语言是什么时候发布的？请告诉我具体的年份。"

[Line 64-68] try: 开始异常捕获

[Line 65] result2 = agent.run(search_question)
    └── [demo/my_react_agent.py:60-105] MyReActAgent.run() 执行流程

    │==== 第 1 步 ====

    ├── 构建提示词
    │   └── tools_desc = "- calculate: 执行数学计算，支持基本的四则运算\n- search: 搜索互联网信息"

    ├── 调用 LLM
    │   └── LLM 响应:
    │       """
    │       Thought: 用户询问 Python 编程语言的发布年份。这需要搜索互联网来获取准确信息。我应该使用 search 工具。
    │       Action: search[Python编程语言发布年份]
    │       """

    ├── 解析输出
    │   ├── thought = "用户询问 Python 编程语言的发布年份..."
    │   └── action = "search[Python编程语言发布年份]"

    ├── 检查是否完成
    │   └── action.startswith("Finish") → False

    ├── 执行工具
    │   ├── tool_name = "search"
    │   ├── tool_input = "Python编程语言发布年份"
    │   │
    │   └── observation = tool_registry.execute_tool("search", "Python编程语言发布年份")
    │       └── [tools/registry.py:132-220] execute_tool() 执行流程
    │           ├── 检查熔断器 → is_open("search") → False
    │           │
    │           ├── 查找工具 → "search" in self._functions → True
    │           ├── func = self._functions["search"]["func"]
    │           │
    │           ├── result = func("Python编程语言发布年份")
    │           │   └── [tools/builtin/search.py:42-82] search() 执行流程
    │           │       ├── [Line 49-51] api_key = os.getenv("SERPAPI_API_KEY")
    │           │       │   └── api_key = "xxxxx" (假设存在)
    │           │       │
    │           │       ├── [Line 53-59] params = {
    │           │       │   ├── "engine": "google",
    │           │       │   ├── "q": "Python编程语言发布年份",
    │           │       │   ├── "api_key": "xxxxx",
    │           │       │   ├── "gl": "cn",
    │           │       │   └── "hl": "zh-cn"
    │           │       │   }
    │           │       │
    │           │       ├── [Line 61] client = SerpApiClient(params)
    │           │       │
    │           │       ├── [Line 62] results = client.get_dict()
    │           │       │   └── 调用 SerpApi 获取搜索结果
    │           │       │
    │           │       ├── [Line 65-77] 解析搜索结果
    │           │       │   ├── if "answer_box_list" in results: → False
    │           │       │   ├── elif "answer_box" in results and "answer" in results["answer_box"]: → False
    │           │       │   ├── elif "knowledge_graph" in results and "description" in results["knowledge_graph"]: → True
    │           │       │   │   └── return results["knowledge_graph"]["description"]
    │           │       │   │       └── "Python 编程语言首次发布于 1991 年。由 Guido van Rossum 创建..."
    │           │       │   │
    │           │       │   └── 返回搜索结果字符串
    │           │       │
    │           │       └── 返回 "Python 编程语言首次发布于 1991 年。由 Guido van Rossum 创建..."
    │           │
    │           ├── 包装为 ToolResponse
    │           │   └── ToolResponse.success(
    │           │       text="Python 编程语言首次发布于 1991 年...",
    │           │       data={"output": "..."},
    │           │       stats={"time_ms": ...},
    │           │       context={"tool_name": "search", "input": "..."}
    │           │   )
    │           │
    │           └── 返回 ToolResponse 对象
    │
    ├── 记录历史
    │   ├── current_history.append("Action: search[Python编程语言发布年份]")
    │   └── current_history.append("Observation: Python 编程语言首次发布于 1991 年...")

    │==== 第 2 步 ====

    ├── 构建提示词 (包含历史)
    │   └── history_str 包含上一步的 Action 和 Observation

    ├── 调用 LLM
    │   └── LLM 响应:
    │       """
    │       Thought: 搜索结果显示 Python 首次发布于 1991 年。现在我有足够的信息来回答用户的问题。
    │       Action: Finish[Python 编程语言是在 1991 年发布的。由 Guido van Rossum 创建。]
    │       """

    ├── 解析输出
    │   ├── thought = "搜索结果显示 Python 首次发布于 1991 年..."
    │   └── action = "Finish[Python 编程语言是在 1991 年发布的...]"

    ├── 检查是否完成
    │   └── action.startswith("Finish") → True

    ├── 提取答案
    │   └── final_answer = "Python 编程语言是在 1991 年发布的。由 Guido van Rossum 创建。"

    ├── 保存消息到历史
    │   ├── add_message(Message(search_question, "user"))
    │   └── add_message(Message(final_answer, "assistant"))

    └── 返回结果
        └── "Python 编程语言是在 1991 年发布的。由 Guido van Rossum 创建。"

result2 = "Python 编程语言是在 1991 年发布的。由 Guido van Rossum 创建。"

[Line 66] print(f"\n🎯 测试2结果: {result2}")
    └── 输出: (换行)🎯 测试2结果: Python 编程语言是在 1991 年发布的。由 Guido van Rossum 创建。
```

---

# 测试用例 3: 复合推理问题 - 代码执行流程

## 输入
```python
complex_question = "如果一个班级有30个学生，其中60%是女生，那么男生有多少人？请先计算女生人数，再计算男生人数。"
```

## 代码执行流程 (简化版)

```
[Line 71-72] print("\n🧠 测试3：复合推理问题")
    └── 输出: (换行)🧠 测试3：复合推理问题

[Line 72] complex_question = "..."

[Line 74-78] try: 开始异常捕获

[Line 75] result3 = agent.run(complex_question)
    └── [demo/my_react_agent.py:60-105] MyReActAgent.run() 执行流程

    │==== 第 1 步：计算女生人数 ====

    ├── 构建提示词 (问题: "如果一个班级有30个学生...")

    ├── 调用 LLM
    │   └── LLM 响应:
    │       """
    │       Thought: 用户要求我计算班级中女生和男生的人数。首先需要计算女生人数：30 × 60%。
    │       Action: calculate[30 * 0.6]
    │       """

    ├── 解析输出
    │   └── action = "calculate[30 * 0.6]"

    ├── 执行工具
    │   └── observation = tool_registry.execute_tool("calculate", "30 * 0.6")
    │       └── 返回: "计算结果: 18.0"

    ├── 记录历史
    │   └── current_history = [
    │       "Action: calculate[30 * 0.6]",
    │       "Observation: 计算结果: 18.0"
    │      ]

    │==== 第 2 步：计算男生人数 ====

    ├── 构建提示词 (包含第1步的历史)

    ├── 调用 LLM
    │   └── LLM 响应:
    │       """
    │       Thought: 女生有 18 人。现在需要计算男生人数：30 - 18 = 12。
    │       Action: calculate[30 - 18]
    │       """

    ├── 解析输出
    │   └── action = "calculate[30 - 18]"

    ├── 执行工具
    │   └── observation = tool_registry.execute_tool("calculate", "30 - 18")
    │       └── 返回: "计算结果: 12"

    ├── 记录历史
    │   └── current_history = [
    │       "Action: calculate[30 * 0.6]",
    │       "Observation: 计算结果: 18.0",
    │       "Action: calculate[30 - 18]",
    │       "Observation: 计算结果: 12"
    │      ]

    │==== 第 3 步：给出最终答案 ====

    ├── 构建提示词 (包含第1、2步的历史)

    ├── 调用 LLM
    │   └── LLM 响应:
    │       """
    │       Thought: 我已经计算出女生有 18 人，男生有 12 人。现在可以回答用户的问题了。
    │       Action: Finish[班级中女生有 18 人，男生有 12 人。计算过程：女生人数 = 30 × 60% = 18 人；男生人数 = 30 - 18 = 12 人。]
    │       """

    ├── 解析输出
    │   └── action = "Finish[班级中女生有 18 人，男生有 12 人...]"

    ├── 检查是否完成
    │   └── action.startswith("Finish") → True

    ├── 提取答案
    │   └── final_answer = "班级中女生有 18 人，男生有 12 人。计算过程：女生人数 = 30 × 60% = 18 人；男生人数 = 30 - 18 = 12 人。"

    ├── 保存消息到历史
    │   ├── add_message(Message(complex_question, "user"))
    │   └── add_message(Message(final_answer, "assistant"))

    └── 返回结果
        └── "班级中女生有 18 人，男生有 12 人。计算过程：女生人数 = 30 × 60% = 18 人；男生人数 = 30 - 18 = 12 人。"

result3 = "班级中女生有 18 人，男生有 12 人。计算过程：女生人数 = 30 × 60% = 18 人；男生人数 = 30 - 18 = 12 人。"

[Line 76] print(f"\n🎯 测试3结果: {result3}")
    └── 输出: (换行)🎯 测试3结果: 班级中女生有 18 人，男生有 12 人。计算过程：女生人数 = 30 × 60% = 18 人；男生人数 = 30 - 18 = 12 人。
```

---

# 测试用例 4: 自定义提示词测试 - 代码执行流程

## 输入
```python
math_question = "计算 15 × 8 + 32 ÷ 4 的结果"
```

## 代码执行流程

```
[Line 147] test_custom_prompt()
    └── [demo/test_react_agent.py:92-140] test_custom_prompt() 执行流程

    ├── [Line 95-97] print("\n" + "="*60)
    │   └── 输出: (换行)============================================================

    ├── [Line 96] print("测试自定义提示词的 MyReActAgent")
    │   └── 输出: 测试自定义提示词的 MyReActAgent

    ├── [Line 97] print("="*60)
    │   └── 输出: ============================================================

    │--- 创建新的 LLM 和 ToolRegistry ---

    ├── [Line 100] llm = HelloAgentsLLM()
    │   └── 同测试1的初始化流程

    ├── [Line 101] tool_registry = ToolRegistry()
    │   └── 同测试1的初始化流程

    │--- 注册计算器工具 ---

    ├── [Line 104-106] from tiny_agents.tools.builtin.calculator import calculate
    │   └── 导入 calculate 函数

    ├── [Line 106] tool_registry.register_function("calculate", "执行数学计算，支持基本的四则运算", calculate)
    │   └── 同测试1的注册流程

    │--- 创建自定义提示词 ---

    ├── [Line 110-121] custom_prompt = """你是一个数学专家AI助手。

可用工具：{tools}

请按以下格式回应：
Thought: [你的思考]
Action: [tool_name[input] 或 Finish[答案]]

问题：{question}
历史：{history}

开始："""

    │--- 创建自定义提示词 Agent ---

    ├── [Line 124-130] custom_agent = MyReActAgent(
            name="数学专家助手",
            llm=llm,
            tool_registry=tool_registry,
            max_steps=3,  # 注意：这里是 3 而不是 5
            custom_prompt=custom_prompt
        )
        └── [demo/my_react_agent.py:43-58] MyReActAgent.__init__() 执行流程
            ├── super().__init__(...) (同测试1)
            ├── self.tool_registry = tool_registry
            ├── self.max_steps = 3  # 注意这里是 3
            ├── self.current_history = []
            └── self.prompt_template = custom_prompt  # 使用自定义提示词

    │--- 执行测试 ---

    ├── [Line 134] math_question = "计算 15 × 8 + 32 ÷ 4 的结果"

    ├── [Line 136-140] try: 开始异常捕获

    ├── [Line 137] result = custom_agent.run(math_question)
        └── [demo/my_react_agent.py:60-105] MyReActAgent.run() 执行流程

        │==== 第 1 步 ====

        ├── 构建提示词 (使用自定义模板)
        │   └── prompt = custom_prompt.format(
                tools="calculate: 执行数学计算，支持基本的四则运算",
                question="计算 15 × 8 + 32 ÷ 4 的结果",
                history=""
            )
            └── 填充后的提示词:
                """
                你是一个数学专家AI助手。

                可用工具：calculate: 执行数学计算，支持基本的四则运算

                请按以下格式回应：
                Thought: [你的思考]
                Action: [tool_name[input] 或 Finish[答案]]

                问题：计算 15 × 8 + 32 ÷ 4 的结果
                历史：

                开始：
                """

        ├── 调用 LLM
        │   └── LLM 响应 (使用自定义提示词，更简洁):
        │       """
        │       Thought: 需要计算 15 × 8 + 32 ÷ 4
        │       Action: calculate[15 * 8 + 32 / 4]
        │       """

        ├── 执行工具
        │   └── observation = tool_registry.execute_tool("calculate", "15 * 8 + 32 / 4")
        │       └── 返回: "计算结果: 128.0"

        ├── 记录历史
        │   └── current_history = [
                "Action: calculate[15 * 8 + 32 / 4]",
                "Observation: 计算结果: 128.0"
               ]

        │==== 第 2 步 ====

        ├── 构建提示词 (包含历史)

        ├── 调用 LLM
        │   └── LLM 响应:
        │       """
        │       Thought: 计算结果是 128.0
        │       Action: Finish[15 × 8 + 32 ÷ 4 = 128]
        │       """

        ├── 解析输出
        │   └── action = "Finish[15 × 8 + 32 ÷ 4 = 128]"

        ├── 检查是否完成
        │   └── action.startswith("Finish") → True

        ├── 提取答案
        │   └── final_answer = "15 × 8 + 32 ÷ 4 = 128"

        ├── 保存消息到历史
        │   ├── add_message(Message(math_question, "user"))
        │   └── add_message(Message(final_answer, "assistant"))

        └── 返回结果
            └── "15 × 8 + 32 ÷ 4 = 128"

    result = "15 × 8 + 32 ÷ 4 = 128"

    ├── [Line 138] print(f"\n🎯 自定义提示词测试结果: {result}")
    │   └── 输出: (换行)🎯 自定义提示词测试结果: 15 × 8 + 32 ÷ 4 = 128

    ├── [Line 139-140] except Exception as e:
    │   └── 无异常，跳过

    └── 返回 None

[Line 149] print("\n✨ 所有测试完成！")
    └── 输出: (换行)✨ 所有测试完成！

[SCRIPT END] 程序执行完毕
```

---

# 关键数据结构变化追踪

## HelloAgentsLLM 实例状态变化

```
初始化后:
{
    model: "GLM-4.7",
    provider: "zhipu",
    api_key: "sk-xxxxx",
    base_url: "https://open.bigmodel.cn/api/paas/v4",
    temperature: 0.7,
    max_tokens: None,
    timeout: 60,
    _client: OpenAI(...)
}
```

## ToolRegistry 实例状态变化

```
初始化后:
{
    _tools: {},
    _functions: {},
    read_metadata_cache: {},
    circuit_breaker: CircuitBreaker {
        failure_threshold: 3,
        recovery_timeout: 300,
        enabled: True,
        failure_counts: {},
        open_timestamps: {}
    }
}

注册 calculate 后:
{
    _tools: {},
    _functions: {
        "calculate": {
            "description": "执行数学计算，支持基本的四则运算",
            "func": <function calculate at 0x...>
        }
    },
    ...
}

注册 search 后:
{
    _tools: {},
    _functions: {
        "calculate": {...},
        "search": {
            "description": "搜索互联网信息",
            "func": <function search at 0x...>
        }
    },
    ...
}
```

## MyReActAgent 实例状态变化

```
初始化后:
{
    name: "我的推理行动助手",
    llm: <HelloAgentsLLM 实例>,
    tool_registry: <ToolRegistry 实例>,
    max_steps: 5,
    current_history: [],
    prompt_template: MY_REACT_PROMPT
}

测试1执行后 (第1步):
{
    current_history: [
        "Action: calculate[(25 + 15) * 3 - 8]",
        "Observation: 计算结果: 112"
    ]
}

测试1执行后 (第2步 - 完成):
{
    current_history: [
        "Action: calculate[(25 + 15) * 3 - 8]",
        "Observation: 计算结果: 112"
    ],
    history_manager: [
        Message("请帮我计算：(25 + 15) * 3 - 8 的结果是多少？", "user"),
        Message("计算结果是 112。具体计算过程是：...", "assistant")
    ]
}
```

## CircuitBreaker 状态变化

```
初始化后:
{
    failure_counts: {},
    open_timestamps: {}
}

测试1执行后 (calculate 成功):
{
    failure_counts: {
        "calculate": 0  # 重置为0
    },
    open_timestamps: {}
}
```

---

# 执行时间线 (毫秒级)

```
T0:     程序开始
T50:    load_dotenv() 完成
T100:   HelloAgentsLLM 初始化完成
T150:   ToolRegistry 初始化完成
T200:   calculate 工具注册完成
T250:   search 工具注册完成
T300:   MyReActAgent 初始化完成

T1000:  测试1开始
        T1050: 第1步 - 构建提示词
        T1100: 第1步 - 调用 LLM (API 请求)
        T3500: 第1步 - LLM 响应返回
        T3550: 第1步 - 解析输出
        T3600: 第1步 - 执行 calculate 工具
        T3650: 第1步 - 计算完成 (112ms)
        T3700: 第2步 - 构建提示词
        T3750: 第2步 - 调用 LLM (API 请求)
        T5500: 第2步 - LLM 响应返回
        T5550: 第2步 - 解析输出 (Finish)
        T5600: 第2步 - 保存历史
T5650:  测试1完成

T6000:  测试2开始
        T6050: 第1步 - 构建提示词
        T6100: 第1步 - 调用 LLM
        T8000: 第1步 - LLM 响应返回
        T8050: 第1步 - 执行 search 工具
        T9000: 第1步 - 搜索 API 返回结果
        T9050: 第2步 - 构建提示词
        T9100: 第2步 - 调用 LLM
        T10500: 第2步 - LLM 响应返回 (Finish)
T10550: 测试2完成

T11000: 测试3开始
        T11050: 第1步 - 构建提示词
        T11100: 第1步 - 调用 LLM
        T12500: 第1步 - LLM 响应返回
        T12550: 第1步 - 执行 calculate[30*0.6]
        T12600: 第1步 - 计算完成 (18.0)
        T12650: 第2步 - 构建提示词
        T12700: 第2步 - 调用 LLM
        T13800: 第2步 - LLM 响应返回
        T13850: 第2步 - 执行 calculate[30-18]
        T13900: 第2步 - 计算完成 (12)
        T13950: 第3步 - 构建提示词
        T14000: 第3步 - 调用 LLM
        T15200: 第3步 - LLM 响应返回 (Finish)
T15250: 测试3完成

T20000: test_custom_prompt() 开始
T20500:  新的 HelloAgentsLLM 初始化
T21000:  新的 ToolRegistry 初始化
T21500:  calculate 工具注册
T22000:  custom_prompt 定义
T22500:  custom_agent 初始化 (max_steps=3)

T25000: 自定义提示词测试开始
        T25050: 第1步 - 构建提示词 (使用自定义模板)
        T25100: 第1步 - 调用 LLM
        T26500: 第1步 - LLM 响应返回
        T26550: 第1步 - 执行 calculate[15*8+32/4]
        T26600: 第1步 - 计算完成 (128.0)
        T26650: 第2步 - 构建提示词
        T26700: 第2步 - 调用 LLM
        T27800: 第2步 - LLM 响应返回 (Finish)
T27850: 自定义提示词测试完成

T28000: 程序结束
```

---

# 总结

本文档详细记录了 `demo/test_react_agent.py` 四个测试用例的完整代码执行调用链，包括：

1. **精确到代码行的执行流程**
2. **每个方法的内部执行细节**
3. **参数传递和返回值**
4. **条件判断和分支逻辑**
5. **数据结构的状态变化**
6. **执行时间线估算**

这个文档可以作为理解 ReAct Agent 工作原理的完整参考。
