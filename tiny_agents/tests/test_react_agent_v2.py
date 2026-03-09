# test_react_agent_v2.py
"""ReActAgent 测试脚本 v2 - 直接测试核心 ReActAgent 类"""

from dotenv import load_dotenv
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.core.message import Message
from tiny_agents.agents.react_agent import ReActAgent, DEFAULT_REACT_PROMPT
from tiny_agents.tools.registry import ToolRegistry
from tiny_agents.tools.builtin.calculator import CalculatorTool

# 加载环境变量
load_dotenv()

# 创建LLM实例
llm = HelloAgentsLLM()

# ==================== 测试1：基础 ReActAgent（默认配置） ====================
print("\n" + "="*80)
print("测试1：基础 ReActAgent（默认配置）")
print("="*80)

# 创建工具注册表并注册计算器工具
tool_registry_1 = ToolRegistry()
calculator = CalculatorTool()
tool_registry_1.register_tool(calculator)

agent1 = ReActAgent(
    name="基础推理助手",
    llm=llm,
    tool_registry=tool_registry_1
)

result1 = agent1.run("请帮我计算：25 + 15 等于多少？")
print(f"\n🎯 最终结果: {result1}")
print(f"📝 对话历史: {len(agent1.get_history())} 条消息")

# ==================== 测试2：自定义最大步数 ====================
print("\n" + "="*80)
print("测试2：自定义最大步数（3步）")
print("="*80)

tool_registry_2 = ToolRegistry()
tool_registry_2.register_tool(calculator)

agent2 = ReActAgent(
    name="快速推理助手",
    llm=llm,
    tool_registry=tool_registry_2,
    max_steps=3
)

result2 = agent2.run("计算：(10 + 5) * 2 的结果")
print(f"\n🎯 最终结果: {result2}")

# ==================== 测试3：自定义提示词模板 ====================
print("\n" + "="*80)
print("测试3：自定义提示词模板")
print("="*80)

tool_registry_3 = ToolRegistry()
tool_registry_3.register_tool(calculator)

custom_prompt = """你是一个数学专家AI助手。

## 可用工具
{tools}

## 回应格式
思考: [你的分析]
行动: tool_name[参数] 或 Finish[答案]

## 问题
{question}

## 历史
{history}

请开始："""

agent3 = ReActAgent(
    name="数学专家助手",
    llm=llm,
    tool_registry=tool_registry_3,
    custom_prompt=custom_prompt
)

result3 = agent3.run("计算 100 除以 4 等于多少？")
print(f"\n🎯 最终结果: {result3}")

# ==================== 测试4：多工具场景 ====================
print("\n" + "="*80)
print("测试4：多工具场景")
print("="*80)

tool_registry_4 = ToolRegistry()

# 注册计算器工具
tool_registry_4.register_tool(calculator)

# 注册函数工具（模拟搜索）
def mock_search(query: str) -> str:
    """模拟搜索功能"""
    return f"搜索结果：关于'{query}'的信息是...（模拟结果）"

tool_registry_4.register_function(mock_search, name="search", description="搜索互联网信息")

agent4 = ReActAgent(
    name="多工具助手",
    llm=llm,
    tool_registry=tool_registry_4,
    max_steps=5
)

# 测试使用计算器
result4 = agent4.run("计算：8 * 7 + 15")
print(f"\n🎯 最终结果: {result4}")

# ==================== 测试5：连续多任务处理 ====================
print("\n" + "="*80)
print("测试5：连续多任务处理")
print("="*80)

tool_registry_5 = ToolRegistry()
tool_registry_5.register_tool(calculator)

multi_task_agent = ReActAgent(
    name="多任务推理助手",
    llm=llm,
    tool_registry=tool_registry_5,
    max_steps=3
)

# 任务1
print("\n--- 任务1 ---")
result5a = multi_task_agent.run("计算 15 + 20")
print(f"结果: {result5a}")

# 任务2（独立的任务，current_history 会重置）
print("\n--- 任务2 ---")
result5b = multi_task_agent.run("计算 30 - 12")
print(f"结果: {result5b}")

print(f"\n总对话历史: {len(multi_task_agent.get_history())} 条消息")

# ==================== 测试6：达到最大步数限制 ====================
print("\n" + "="*80)
print("测试6：达到最大步数限制")
print("="*80)

tool_registry_6 = ToolRegistry()
tool_registry_6.register_tool(calculator)

# 设置较小的最大步数
agent6 = ReActAgent(
    name="限制步数助手",
    llm=llm,
    tool_registry=tool_registry_6,
    max_steps=2
)

result6 = agent6.run("计算：(100 + 50) / 5 - 10")
print(f"\n🎯 结果: {result6}")
print("(如果步数不足，可能会返回限制消息)")

# ==================== 测试7：解析方法测试 ====================
print("\n" + "="*80)
print("测试7：解析方法测试")
print("="*80)

tool_registry_7 = ToolRegistry()
tool_registry_7.register_tool(calculator)

agent7 = ReActAgent(
    name="解析测试助手",
    llm=llm,
    tool_registry=tool_registry_7,
    max_steps=1
)

# 测试 _parse_output 方法
print("\n--- 测试 _parse_output ---")
test_output_1 = "Thought: 我需要计算这个表达式\nAction: calculate[15 + 20]"
thought_1, action_1 = agent7._parse_output(test_output_1)
print(f"输入: {test_output_1}")
print(f"思考: {thought_1}")
print(f"行动: {action_1}")

test_output_2 = "Thought: 我已有足够信息\nAction: Finish[答案是35]"
thought_2, action_2 = agent7._parse_output(test_output_2)
print(f"\n输入: {test_output_2}")
print(f"思考: {thought_2}")
print(f"行动: {action_2}")

# 测试 _parse_action 方法
print("\n--- 测试 _parse_action ---")
test_action_1 = "calculate[25 + 15]"
tool_name_1, tool_input_1 = agent7._parse_action(test_action_1)
print(f"输入: {test_action_1}")
print(f"工具名: {tool_name_1}")
print(f"工具输入: {tool_input_1}")

test_action_2 = "Finish[最终答案]"
tool_name_2, tool_input_2 = agent7._parse_action(test_action_2)
print(f"\n输入: {test_action_2}")
print(f"工具名: {tool_name_2}")
print(f"工具输入: {tool_input_2}")

# 测试 _parse_action_input 方法
print("\n--- 测试 _parse_action_input ---")
test_finish_1 = "Finish[计算结果是40]"
input_1 = agent7._parse_action_input(test_finish_1)
print(f"输入: {test_finish_1}")
print(f"提取的答案: {input_1}")

# ==================== 测试8：空工具注册表 ====================
print("\n" + "="*80)
print("测试8：空工具注册表")
print("="*80)

# 创建空工具注册表
empty_registry = ToolRegistry()

agent8 = ReActAgent(
    name="无工具助手",
    llm=llm,
    tool_registry=empty_registry,
    max_steps=2
)

result8 = agent8.run("你好，请介绍一下自己")
print(f"\n🎯 结果: {result8[:200]}...")
print("(没有工具时，Agent仍然可以回答简单问题)")

# ==================== 测试9：清空历史测试 ====================
print("\n" + "="*80)
print("测试9：清空历史测试")
print("="*80)

tool_registry_9 = ToolRegistry()
tool_registry_9.register_tool(calculator)

agent9 = ReActAgent(
    name="可清空助手",
    llm=llm,
    tool_registry=tool_registry_9,
    max_steps=2
)

# 执行任务
agent9.run("计算 5 + 3")
print(f"\n清空前 - 对话历史: {len(agent9.get_history())} 条")

# 清空历史
agent9.clear_history()
print(f"清空后 - 对话历史: {len(agent9.get_history())} 条")

# 执行新任务
agent9.run("计算 10 * 2")
print(f"新任务后 - 对话历史: {len(agent9.get_history())} 条")

# ==================== 测试10：并行多个独立 Agent ====================
print("\n" + "="*80)
print("测试10：并行多个独立 ReActAgent")
print("="*80)

# 创建三个独立的工具注册表和Agent
registry_a = ToolRegistry()
registry_a.register_tool(calculator)

registry_b = ToolRegistry()
registry_b.register_tool(calculator)

registry_c = ToolRegistry()
registry_c.register_tool(calculator)

agent_a = ReActAgent(name="助手A", llm=llm, tool_registry=registry_a, max_steps=1)
agent_b = ReActAgent(name="助手B", llm=llm, tool_registry=registry_b, max_steps=1)
agent_c = ReActAgent(name="助手C", llm=llm, tool_registry=registry_c, max_steps=1)

question = "计算 2 + 3"

print("\n--- 助手A ---")
result_a = agent_a.run(question)
print(f"结果: {result_a}")

print("\n--- 助手B ---")
result_b = agent_b.run(question)
print(f"结果: {result_b}")

print("\n--- 助手C ---")
result_c = agent_c.run(question)
print(f"结果: {result_c}")

# 验证独立性
print(f"\n助手A历史: {len(agent_a.get_history())} 条")
print(f"助手B历史: {len(agent_b.get_history())} 条")
print(f"助手C历史: {len(agent_c.get_history())} 条")

# ==================== 测试11：DEFAULT_REACT_PROMPT 测试 ====================
print("\n" + "="*80)
print("测试11：默认提示词模板测试")
print("="*80)

print("\n--- DEFAULT_REACT_PROMPT 预览 ---")
print(DEFAULT_REACT_PROMPT[:300] + "...")

print("\n--- 模板变量 ---")
print("必需变量: {tools}, {question}, {history}")

# ==================== 测试12：复杂多步计算 ====================
print("\n" + "="*80)
print("测试12：复杂多步计算")
print("="*80)

tool_registry_12 = ToolRegistry()
tool_registry_12.register_tool(calculator)

agent12 = ReActAgent(
    name="复杂计算助手",
    llm=llm,
    tool_registry=tool_registry_12,
    max_steps=5
)

complex_task = "请计算：((15 + 10) * 2) / 5 的结果"
result12 = agent12.run(complex_task)
print(f"\n🎯 最终结果: {result12}")

# 显示步骤历史
print(f"\n--- 执行步骤历史 ---")
for i, step in enumerate(agent12.current_history, 1):
    print(f"{i}. {step[:100]}...")

# ==================== 测试13：边界情况 - 无效Action格式 ====================
print("\n" + "="*80)
print("测试13：边界情况 - 无效Action格式")
print("="*80)

tool_registry_13 = ToolRegistry()
tool_registry_13.register_tool(calculator)

agent13 = ReActAgent(
    name="边界测试助手",
    llm=llm,
    tool_registry=tool_registry_13,
    max_steps=3
)

# 测试可能产生无效格式的任务
result13 = agent13.run("你好")
print(f"\n🎯 结果: {result13[:200]}...")

# ==================== 测试14：注册多个函数工具 ====================
print("\n" + "="*80)
print("测试14：注册多个函数工具")
print("="*80)

tool_registry_14 = ToolRegistry()

# 注册多个函数工具
def add(a: str) -> str:
    """加法"""
    try:
        nums = [float(x.strip()) for x in a.split('+')]
        return str(sum(nums))
    except:
        return "计算错误"

def multiply(a: str) -> str:
    """乘法"""
    try:
        nums = [float(x.strip()) for x in a.split('*')]
        result = 1
        for num in nums:
            result *= num
        return str(result)
    except:
        return "计算错误"

def get_length(text: str) -> str:
    """获取文本长度"""
    return f"文本长度: {len(text)}"

tool_registry_14.register_function(add, name="add", description="执行加法运算")
tool_registry_14.register_function(multiply, name="multiply", description="执行乘法运算")
tool_registry_14.register_function(get_length, name="get_length", description="获取文本长度")

agent14 = ReActAgent(
    name="多函数工具助手",
    llm=llm,
    tool_registry=tool_registry_14,
    max_steps=4
)

result14 = agent14.run("计算 5 + 3 + 2")
print(f"\n🎯 结果: {result14}")

# ==================== 测试15：current_history 内容测试 ====================
print("\n" + "="*80)
print("测试15：current_history 内容测试")
print("="*80)

tool_registry_15 = ToolRegistry()
tool_registry_15.register_tool(calculator)

agent15 = ReActAgent(
    name="历史内容助手",
    llm=llm,
    tool_registry=tool_registry_15,
    max_steps=3
)

agent15.run("计算 10 + 5")

print("\n--- current_history 内容 ---")
for i, entry in enumerate(agent15.current_history, 1):
    print(f"{i}. {entry[:150]}...")

# ==================== 总结统计 ====================
print("\n" + "="*80)
print("测试总结")
print("="*80)

print("\n✅ 所有测试完成！")
print("\n测试覆盖:")
print("  1. 基础 ReActAgent（默认配置）")
print("  2. 自定义最大步数")
print("  3. 自定义提示词模板")
print("  4. 多工具场景")
print("  5. 连续多任务处理")
print("  6. 达到最大步数限制")
print("  7. 解析方法测试")
print("  8. 空工具注册表")
print("  9. 清空历史测试")
print("  10. 并行多个独立 Agent")
print("  11. DEFAULT_REACT_PROMPT 测试")
print("  12. 复杂多步计算")
print("  13. 边界情况 - 无效Action格式")
print("  14. 注册多个函数工具")
print("  15. current_history 内容测试")

print("\n" + "="*80)
