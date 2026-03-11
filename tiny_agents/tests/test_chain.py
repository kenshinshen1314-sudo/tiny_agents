# test_chain.py
"""ToolChain 和 ToolChainManager 测试脚本"""

from dotenv import load_dotenv
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.tools.registry import ToolRegistry
from tiny_agents.tools.chain import (
    ToolChain,
    ToolChainManager,
    create_research_chain,
    create_simple_chain
)
from tiny_agents.tools.builtin.calculator import CalculatorTool

# 加载环境变量
load_dotenv()

# 创建LLM实例（虽然chain不需要，但为了完整性）
llm = HelloAgentsLLM()

# ==================== 测试1：基础 ToolChain（单步骤） ====================
print("\n" + "="*80)
print("测试1：基础 ToolChain（单步骤）")
print("="*80)

# 创建工具注册表并注册计算器
registry_1 = ToolRegistry()
calculator = CalculatorTool()
registry_1.register_tool(calculator)

# 为了兼容性，也注册为函数工具
def my_calculator(expr: str) -> str:
    """计算器函数包装"""
    result = calculator.run({"input": expr})
    return result.text if hasattr(result, 'text') else str(result)

registry_1.register_function(my_calculator, name="my_calculator", description="计算器工具")

# 创建单步骤工具链
chain1 = ToolChain(
    name="simple_calculation",
    description="简单的计算工具链"
)

chain1.add_step(
    tool_name="my_calculator",
    input_template="{input}",
    output_key="result"
)

result1 = chain1.execute(registry_1, "15 + 25")
print(f"\n🎯 执行结果: {result1}")

# ==================== 测试2：多步骤 ToolChain ====================
print("\n" + "="*80)
print("测试2：多步骤 ToolChain")
print("="*80)

registry_2 = ToolRegistry()
registry_2.register_tool(calculator)
registry_2.register_function(my_calculator, name="my_calculator", description="计算器工具")

chain2 = ToolChain(
    name="multi_step_calculation",
    description="多步骤计算工具链"
)

# 步骤1：第一次计算
chain2.add_step(
    tool_name="my_calculator",
    input_template="{input}",
    output_key="step1_result"
)

# 步骤2：基于步骤1的结果进行第二次计算
chain2.add_step(
    tool_name="my_calculator",
    input_template="({step1_result}) * 2",
    output_key="step2_result"
)

# 步骤3：基于步骤2的结果进行第三次计算
chain2.add_step(
    tool_name="my_calculator",
    input_template="({step2_result}) + 10",
    output_key="final_result"
)

result2 = chain2.execute(registry_2, "5 + 3")
print(f"\n🎯 最终执行结果: {result2}")

# ==================== 测试3：变量替换测试 ====================
print("\n" + "="*80)
print("测试3：变量替换测试")
print("="*80)

registry_3 = ToolRegistry()
registry_3.register_tool(calculator)
registry_3.register_function(my_calculator, name="my_calculator", description="计算器工具")

chain3 = ToolChain(
    name="variable_test",
    description="变量替换测试"
)

# 使用多个变量
chain3.add_step(
    tool_name="my_calculator",
    input_template="{input}",
    output_key="first_result"
)

chain3.add_step(
    tool_name="my_calculator",
    input_template="{first_result} * {multiplier}",
    output_key="second_result"
)

# 提供自定义上下文
custom_context = {"multiplier": "5"}
result3 = chain3.execute(registry_3, "10 + 2", context=custom_context)
print(f"\n🎯 执行结果: {result3}")

# ==================== 测试4：ToolChainManager 基础功能 ====================
print("\n" + "="*80)
print("测试4：ToolChainManager 基础功能")
print("="*80)

registry_4 = ToolRegistry()
registry_4.register_tool(calculator)
registry_4.register_function(my_calculator, name="my_calculator", description="计算器工具")

manager_4 = ToolChainManager(registry_4)

# 注册工具链
chain_a = ToolChain("chain_a", "工具链A")
chain_a.add_step("my_calculator", "{input}", "result_a")

chain_b = ToolChain("chain_b", "工具链B")
chain_b.add_step("my_calculator", "({input}) * 2", "result_b")

manager_4.register_chain(chain_a)
manager_4.register_chain(chain_b)

# 列出工具链
chains = manager_4.list_chains()
print(f"\n已注册的工具链: {chains}")

# 获取工具链信息
info_a = manager_4.get_chain_info("chain_a")
print(f"\n工具链A信息:")
print(f"  名称: {info_a['name']}")
print(f"  描述: {info_a['description']}")
print(f"  步骤数: {info_a['steps']}")
print(f"  步骤详情: {info_a['step_details']}")

# ==================== 测试5：ToolChainManager 执行工具链 ====================
print("\n" + "="*80)
print("测试5：ToolChainManager 执行工具链")
print("="*80)

registry_5 = ToolRegistry()
registry_5.register_tool(calculator)
registry_5.register_function(my_calculator, name="my_calculator", description="计算器工具")

manager_5 = ToolChainManager(registry_5)

# 创建并注册工具链
chain_calc = ToolChain("calc_chain", "计算链")
chain_calc.add_step("my_calculator", "{input}", "calc_result")
manager_5.register_chain(chain_calc)

# 执行工具链
result5 = manager_5.execute_chain("calc_chain", "8 * 7")
print(f"\n🎯 执行结果: {result5}")

# ==================== 测试6：空工具链测试 ====================
print("\n" + "="*80)
print("测试6：空工具链测试")
print("="*80)

registry_6 = ToolRegistry()

empty_chain = ToolChain("empty_chain", "空工具链")
# 不添加任何步骤

result6 = empty_chain.execute(registry_6, "test input")
print(f"\n🎯 空工具链执行结果: {result6}")

# ==================== 测试7：工具不存在的情况 ====================
print("\n" + "="*80)
print("测试7：工具不存在的情况")
print("="*80)

registry_7 = ToolRegistry()

chain7 = ToolChain("missing_tool", "使用不存在工具的链")
chain7.add_step("nonexistent_tool", "{input}", "result")

result7 = chain7.execute(registry_7, "test")
print(f"\n🎯 执行结果: {result7}")

# ==================== 测试8：create_simple_chain 便捷函数 ====================
print("\n" + "="*80)
print("测试8：create_simple_chain 便捷函数")
print("="*80)

registry_8 = ToolRegistry()
registry_8.register_tool(calculator)
registry_8.register_function(my_calculator, name="my_calculator", description="计算器工具")

simple_chain = create_simple_chain()
print(f"\n工具链名称: {simple_chain.name}")
print(f"工具链描述: {simple_chain.description}")
print(f"步骤数: {len(simple_chain.steps)}")

result8 = simple_chain.execute(registry_8, "100 / 4")
print(f"\n🎯 执行结果: {result8}")

# ==================== 测试9：create_research_chain 便捷函数 ====================
print("\n" + "="*80)
print("测试9：create_research_chain 便捷函数")
print("="*80)

registry_9 = ToolRegistry()
registry_9.register_tool(calculator)
registry_9.register_function(my_calculator, name="my_calculator", description="计算器工具")

# 添加一个模拟搜索工具
def mock_search(query: str) -> str:
    return f"搜索结果：关于 '{query}' 的信息..."

registry_9.register_function(mock_search, name="search", description="搜索工具")

research_chain = create_research_chain()
print(f"\n工具链名称: {research_chain.name}")
print(f"工具链描述: {research_chain.description}")
print(f"步骤数: {len(research_chain.steps)}")

result9 = research_chain.execute(registry_9, "Python编程")
print(f"\n🎯 执行结果: {result9}")

# ==================== 测试10：自定义输出键名 ====================
print("\n" + "="*80)
print("测试10：自定义输出键名")
print("="*80)

registry_10 = ToolRegistry()
registry_10.register_tool(calculator)
registry_10.register_function(my_calculator, name="my_calculator", description="计算器工具")

chain10 = ToolChain("custom_keys", "自定义键名测试")

# 使用自定义的输出键名
chain10.add_step("my_calculator", "{input}", "my_custom_output")
chain10.add_step("my_calculator", "({my_custom_output}) + 100", "final_value")

result10 = chain10.execute(registry_10, "50 - 20")
print(f"\n🎯 最终结果: {result10}")

# ==================== 测试11：上下文传递测试 ====================
print("\n" + "="*80)
print("测试11：上下文传递测试")
print("="*80)

registry_11 = ToolRegistry()
registry_11.register_tool(calculator)
registry_11.register_function(my_calculator, name="my_calculator", description="计算器工具")

chain11 = ToolChain("context_test", "上下文测试")

chain11.add_step("my_calculator", "{base_number}", "step1")
chain11.add_step("my_calculator", "({step1}) * {multiplier}", "step2")

# 提供初始上下文
context_11 = {"base_number": "10", "multiplier": "3"}
result11 = chain11.execute(registry_11, "", context=context_11)
print(f"\n🎯 执行结果: {result11}")

# ==================== 测试12：模板变量替换失败的情况 ====================
print("\n" + "="*80)
print("测试12：模板变量替换失败的情况")
print("="*80)

registry_12 = ToolRegistry()
registry_12.register_tool(calculator)
registry_12.register_function(my_calculator, name="my_calculator", description="计算器工具")

chain12 = ToolChain("template_error", "模板错误测试")

# 使用不存在的变量
chain12.add_step("my_calculator", "{nonexistent_var}", "result")

result12 = chain12.execute(registry_12, "test")
print(f"\n🎯 执行结果: {result12}")

# ==================== 测试13：链式调用多个计算 ====================
print("\n" + "="*80)
print("测试13：链式调用多个计算")
print("="*80)

registry_13 = ToolRegistry()
registry_13.register_tool(calculator)
registry_13.register_function(my_calculator, name="my_calculator", description="计算器工具")

chain13 = ToolChain("complex_calculation", "复杂计算链")

# 模拟一个复杂的计算流程：(a + b) * c - d
chain13.add_step("my_calculator", "{a} + {b}", "sum_result")
chain13.add_step("my_calculator", "({sum_result}) * {c}", "multiplied_result")
chain13.add_step("my_calculator", "({multiplied_result}) - {d}", "final_result")

context_13 = {"a": "10", "b": "20", "c": "3", "d": "15"}
result13 = chain13.execute(registry_13, "", context=context_13)
print(f"\n🎯 计算结果: {result13}")
print(f"预期: (10 + 20) * 3 - 15 = 75")

# ==================== 测试14：ToolChainManager 查询功能 ====================
print("\n" + "="*80)
print("测试14：ToolChainManager 查询功能")
print("="*80)

registry_14 = ToolRegistry()
registry_14.register_tool(calculator)
registry_14.register_function(my_calculator, name="my_calculator", description="计算器工具")

manager_14 = ToolChainManager(registry_14)

# 创建多个工具链
chain_x = ToolChain("chain_x", "工具链X")
chain_x.add_step("my_calculator", "{input}", "x_result")

chain_y = ToolChain("chain_y", "工具链Y")
chain_y.add_step("my_calculator", "({input}) * 2", "y_result")

chain_z = ToolChain("chain_z", "工具链Z")
chain_z.add_step("my_calculator", "({input}) / 2", "z_result")

manager_14.register_chain(chain_x)
manager_14.register_chain(chain_y)
manager_14.register_chain(chain_z)

# 列出所有工具链
all_chains = manager_14.list_chains()
print(f"\n所有工具链: {all_chains}")

# 获取每个工具链的信息
for chain_name in all_chains:
    info = manager_14.get_chain_info(chain_name)
    print(f"\n{chain_name}:")
    print(f"  描述: {info['description']}")
    print(f"  步骤数: {info['steps']}")

# ==================== 测试15：执行不存在的工具链 ====================
print("\n" + "="*80)
print("测试15：执行不存在的工具链")
print("="*80)

registry_15 = ToolRegistry()
manager_15 = ToolChainManager(registry_15)

result15 = manager_15.execute_chain("nonexistent_chain", "test input")
print(f"\n🎯 执行结果: {result15}")

# ==================== 测试16：步骤详情查看 ====================
print("\n" + "="*80)
print("测试16：步骤详情查看")
print("="*80)

registry_16 = ToolRegistry()
registry_16.register_tool(calculator)
registry_16.register_function(my_calculator, name="my_calculator", description="计算器工具")

manager_16 = ToolChainManager(registry_16)

chain16 = ToolChain("detailed_chain", "详细步骤链")
chain16.add_step("my_calculator", "{x}", "step1_result")
chain16.add_step("my_calculator", "({step1_result}) * 2", "step2_result")
chain16.add_step("my_calculator", "({step2_result}) + 10", "final_result")

manager_16.register_chain(chain16)

# 获取详细信息
info16 = manager_16.get_chain_info("detailed_chain")
print(f"\n工具链: {info16['name']}")
print(f"描述: {info16['description']}")
print(f"\n步骤详情:")
for i, step in enumerate(info16['step_details'], 1):
    print(f"  步骤{i}:")
    print(f"    工具: {step['tool_name']}")
    print(f"    输入模板: {step['input_template']}")
    print(f"    输出键: {step['output_key']}")

# ==================== 总结统计 ====================
print("\n" + "="*80)
print("测试总结")
print("="*80)

print("\n✅ 所有测试完成！")
print("\n测试覆盖:")
print("  1. 基础 ToolChain（单步骤）")
print("  2. 多步骤 ToolChain")
print("  3. 变量替换测试")
print("  4. ToolChainManager 基础功能")
print("  5. ToolChainManager 执行工具链")
print("  6. 空工具链测试")
print("  7. 工具不存在的情况")
print("  8. create_simple_chain 便捷函数")
print("  9. create_research_chain 便捷函数")
print("  10. 自定义输出键名")
print("  11. 上下文传递测试")
print("  12. 模板变量替换失败的情况")
print("  13. 链式调用多个计算")
print("  14. ToolChainManager 查询功能")
print("  15. 执行不存在的工具链")
print("  16. 步骤详情查看")

print("\n" + "="*80)
