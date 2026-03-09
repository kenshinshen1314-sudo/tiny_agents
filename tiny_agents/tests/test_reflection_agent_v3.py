# test_reflection_agent_v3.py
"""ReflectionAgent 测试脚本 v3 - 直接测试核心 ReflectionAgent 类"""

from dotenv import load_dotenv
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.core.message import Message
from tiny_agents.agents.reflection_agent import ReflectionAgent, DEFAULT_PROMPTS, Memory

# 加载环境变量
load_dotenv()

# 创建LLM实例
llm = HelloAgentsLLM()

# ==================== 测试1：基础 ReflectionAgent（默认配置） ====================
print("\n" + "="*80)
print("测试1：基础 ReflectionAgent（默认配置）")
print("="*80)

agent1 = ReflectionAgent(
    name="基础反思助手",
    llm=llm
)

result1 = agent1.run("用简单的语言解释什么是递归")
print(f"\n🎯 最终结果长度: {len(result1)} 字符")
print(f"📝 对话历史: {len(agent1.get_history())} 条消息")

# ==================== 测试2：自定义迭代次数 ====================
print("\n" + "="*80)
print("测试2：自定义迭代次数（1轮）")
print("="*80)

agent2 = ReflectionAgent(
    name="快速反思助手",
    llm=llm,
    max_iterations=1
)

result2 = agent2.run("写一个Python函数计算斐波那契数列的第n项")
print(f"\n🎯 最终结果长度: {len(result2)} 字符")

# ==================== 测试3：自定义提示词模板 ====================
print("\n" + "="*80)
print("测试3：自定义提示词模板")
print("="*80)

custom_prompts = {
    "initial": """
你是一位Python编程专家。请完成以下任务：

任务: {task}

要求：
1. 代码要简洁高效
2. 包含适当的注释
3. 考虑边界情况

请提供完整的代码实现。
""",
    "reflect": """
你是一位代码审查专家。请审查以下代码：

任务: {task}

代码:
{content}

请从以下角度审查：
1. 代码正确性
2. 性能优化
3. 边界情况处理

如果代码已经很好，请回答"无需改进"。
""",
    "refine": """
请根据反馈改进代码：

任务: {task}
上一版代码:
{last_attempt}
反馈:
{feedback}

请提供改进后的代码。
"""
}

agent3 = ReflectionAgent(
    name="代码反思助手",
    llm=llm,
    max_iterations=2,
    custom_prompts=custom_prompts
)

result3 = agent3.run("实现一个快速排序算法")
print(f"\n🎯 最终结果长度: {len(result3)} 字符")

# ==================== 测试4：多任务连续处理 ====================
print("\n" + "="*80)
print("测试4：多任务连续处理")
print("="*80)

multi_task_agent = ReflectionAgent(
    name="多任务助手",
    llm=llm,
    max_iterations=2
)

# 任务1
print("\n--- 任务1 ---")
result4a = multi_task_agent.run("解释什么是面向对象编程")
print(f"结果1长度: {len(result4a)} 字符")

# 任务2（独立的新任务，记忆会重置）
print("\n--- 任务2 ---")
result4b = multi_task_agent.run("解释什么是函数式编程")
print(f"结果2长度: {len(result4b)} 字符")

# 验证每个任务都有独立的对话历史
print(f"\n总对话历史: {len(multi_task_agent.get_history())} 条消息")

# ==================== 测试5：Memory 类测试 ====================
print("\n" + "="*80)
print("测试5：Memory 类独立测试")
print("="*80)

memory = Memory()

# 添加记录
memory.add_record("execution", "def hello():\n    print('Hello World')")
print("\n📝 添加执行记录")

memory.add_record("reflection", "代码结构简单，但缺少文档注释")
print("📝 添加反思记录")

memory.add_record("execution", "def hello():\n    \"\"\"打印问候语\"\"\"\n    print('Hello World')")
print("📝 添加优化后的执行记录")

# 测试 get_trajectory
print("\n--- 完整轨迹 ---")
trajectory = memory.get_trajectory()
print(trajectory)

# 测试 get_last_execution
print("\n--- 最后一次执行 ---")
last_execution = memory.get_last_execution()
print(last_execution)

# 测试记录列表
print(f"\n--- 记录总数 ---")
print(f"总记录数: {len(memory.records)}")

# ==================== 测试6：不同迭代次数对比 ====================
print("\n" + "="*80)
print("测试6：不同迭代次数对比")
print("="*80)

task = "写一首关于人工智能的短诗"

# 1轮迭代
agent_1_iter = ReflectionAgent(name="1轮助手", llm=llm, max_iterations=1)
result_1 = agent_1_iter.run(task)
print(f"\n--- 1轮迭代 ---")
print(f"结果长度: {len(result_1)} 字符")

# 2轮迭代
agent_2_iter = ReflectionAgent(name="2轮助手", llm=llm, max_iterations=2)
result_2 = agent_2_iter.run(task)
print(f"\n--- 2轮迭代 ---")
print(f"结果长度: {len(result_2)} 字符")

# 3轮迭代
agent_3_iter = ReflectionAgent(name="3轮助手", llm=llm, max_iterations=3)
result_3 = agent_3_iter.run(task)
print(f"\n--- 3轮迭代 ---")
print(f"结果长度: {len(result_3)} 字符")

# ==================== 测试7：提前终止（"无需改进"） ====================
print("\n" + "="*80)
print("测试7：提前终止测试")
print("="*80)

# 使用一个简单任务，可能在第一轮就达到"无需改进"
simple_agent = ReflectionAgent(
    name="简单任务助手",
    llm=llm,
    max_iterations=5  # 设置较大的迭代次数
)

result7 = simple_agent.run("回答：1+1等于几？")
print(f"\n🎯 结果: {result7[:100]}...")
print("(如果提前终止，说明反思认为结果已足够好)")

# ==================== 测试8：清空历史测试 ====================
print("\n" + "="*80)
print("测试8：清空历史测试")
print("="*80)

clear_agent = ReflectionAgent(
    name="可清空助手",
    llm=llm,
    max_iterations=1
)

# 执行任务
clear_agent.run("任务1")
print(f"\n清空前 - 对话历史: {len(clear_agent.get_history())} 条")

# 清空历史
clear_agent.clear_history()
print(f"清空后 - 对话历史: {len(clear_agent.get_history())} 条")

# 执行新任务
clear_agent.run("任务2")
print(f"新任务后 - 对话历史: {len(clear_agent.get_history())} 条")

# ==================== 测试9：并行多个独立 Agent ====================
print("\n" + "="*80)
print("测试9：并行多个独立 ReflectionAgent")
print("="*80)

# 创建多个独立的 ReflectionAgent
agent_a = ReflectionAgent(name="助手A", llm=llm, max_iterations=1)
agent_b = ReflectionAgent(name="助手B", llm=llm, max_iterations=1)
agent_c = ReflectionAgent(name="助手C", llm=llm, max_iterations=1)

task = "用一句话介绍Python"

print("\n--- 助手A ---")
result_a = agent_a.run(task)
print(f"结果: {result_a[:100]}...")

print("\n--- 助手B ---")
result_b = agent_b.run(task)
print(f"结果: {result_b[:100]}...")

print("\n--- 助手C ---")
result_c = agent_c.run(task)
print(f"结果: {result_c[:100]}...")

# 验证独立性
print(f"\n助手A记忆记录数: {len(agent_a.memory.records)}")
print(f"助手B记忆记录数: {len(agent_b.memory.records)}")
print(f"助手C记忆记录数: {len(agent_c.memory.records)}")

# ==================== 测试10：复杂任务多轮迭代 ====================
print("\n" + "="*80)
print("测试10：复杂任务多轮迭代")
print("="*80)

complex_agent = ReflectionAgent(
    name="复杂任务助手",
    llm=llm,
    max_iterations=3
)

complex_task = """
请设计一个学生成绩管理系统，要求：
1. 可以添加学生及其成绩
2. 可以查询学生的平均分
3. 可以按成绩排序
4. 使用面向对象的设计
"""

result10 = complex_agent.run(complex_task)
print(f"\n最终结果长度: {len(result10)} 字符")
print(f"记忆记录数: {len(complex_agent.memory.records)}")

# 显示迭代过程
print("\n--- 迭代过程 ---")
for i, record in enumerate(complex_agent.memory.records):
    record_type = "📝 执行" if record['type'] == 'execution' else "🔍 反思"
    content_len = len(record['content'])
    print(f"{i+1}. {record_type} - 长度: {content_len} 字符")

# ==================== 测试11：DEFAULT_PROMPTS 测试 ====================
print("\n" + "="*80)
print("测试11：默认提示词模板测试")
print("="*80)

print("\n--- DEFAULT_PROMPTS 结构 ---")
print(f"可用提示词: {list(DEFAULT_PROMPTS.keys())}")

print("\n--- initial 模板预览 ---")
print(DEFAULT_PROMPTS['initial'][:100] + "...")

print("\n--- reflect 模板预览 ---")
print(DEFAULT_PROMPTS['reflect'][:100] + "...")

print("\n--- refine 模板预览 ---")
print(DEFAULT_PROMPTS['refine'][:100] + "...")

# ==================== 测试12：空输入和边界情况 ====================
print("\n" + "="*80)
print("测试12：空输入和边界情况测试")
print("="*80)

boundary_agent = ReflectionAgent(
    name="边界测试助手",
    llm=llm,
    max_iterations=1
)

# 12.1 极短任务
print("\n--- 12.1 极短任务 ---")
try:
    result12a = boundary_agent.run("Hi")
    print(f"结果: {result12a[:100] if result12a else '无响应'}...")
except Exception as e:
    print(f"错误: {e}")

# 12.2 特殊字符
print("\n--- 12.2 特殊字符 ---")
try:
    result12b = boundary_agent.run("解释符号: @#$%^&*()")
    print(f"结果: {result12b[:100] if result12b else '无响应'}...")
except Exception as e:
    print(f"错误: {e}")

# 12.3 多行任务
print("\n--- 12.3 多行任务 ---")
try:
    result12c = boundary_agent.run("""
    任务1
    任务2
    任务3
    """)
    print(f"结果: {result12c[:100] if result12c else '无响应'}...")
except Exception as e:
    print(f"错误: {e}")

# ==================== 总结统计 ====================
print("\n" + "="*80)
print("测试总结")
print("="*80)

print("\n✅ 所有测试完成！")
print("\n测试覆盖:")
print("  1. 基础 ReflectionAgent（默认配置）")
print("  2. 自定义迭代次数")
print("  3. 自定义提示词模板")
print("  4. 多任务连续处理")
print("  5. Memory 类独立测试")
print("  6. 不同迭代次数对比")
print("  7. 提前终止（'无需改进'）")
print("  8. 清空历史测试")
print("  9. 并行多个独立 Agent")
print("  10. 复杂任务多轮迭代")
print("  11. DEFAULT_PROMPTS 测试")
print("  12. 空输入和边界情况测试")

print("\n" + "="*80)
