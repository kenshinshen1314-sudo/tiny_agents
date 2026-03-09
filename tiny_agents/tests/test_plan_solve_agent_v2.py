# test_plan_solve_agent_v2.py
"""PlanAndSolveAgent 测试脚本 v2 - 直接测试核心 PlanAndSolveAgent 类"""

from dotenv import load_dotenv
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.core.message import Message
from tiny_agents.agents.plan_solve_agent import (
    PlanAndSolveAgent,
    Planner,
    Executor,
    DEFAULT_PLANNER_PROMPT,
    DEFAULT_EXECUTOR_PROMPT
)

# 加载环境变量
load_dotenv()

# 创建LLM实例
llm = HelloAgentsLLM()

# ==================== 测试1：基础 PlanAndSolveAgent（默认配置） ====================
print("\n" + "="*80)
print("测试1：基础 PlanAndSolveAgent（默认配置）")
print("="*80)

agent1 = PlanAndSolveAgent(
    name="基础规划助手",
    llm=llm
)

result1 = agent1.run("用简单的语言解释什么是递归")
print(f"\n🎯 最终结果长度: {len(result1)} 字符")
print(f"📝 对话历史: {len(agent1.get_history())} 条消息")

# ==================== 测试2：数学问题求解 ====================
print("\n" + "="*80)
print("测试2：数学问题求解")
print("="*80)

agent2 = PlanAndSolveAgent(
    name="数学规划助手",
    llm=llm
)

math_question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"

result2 = agent2.run(math_question)
print(f"\n🎯 最终结果: {result2}")

# ==================== 测试3：自定义提示词模板 ====================
print("\n" + "="*80)
print("测试3：自定义提示词模板")
print("="*80)

custom_prompts = {
    "planner": """
你是数学问题规划专家。请将数学问题分解为清晰的计算步骤。

问题: {question}

请严格按照以下格式输出你的计划:
```python
["步骤1: 描述", "步骤2: 描述", "步骤3: 描述"]
```
""",
    "executor": """
你是数学计算专家。请专注于执行当前步骤。

问题: {question}
完整计划: {plan}
历史: {history}
当前步骤: {current_step}

请只输出数值结果或简短答案:
"""
}

agent3 = PlanAndSolveAgent(
    name="自定义规划助手",
    llm=llm,
    custom_prompts=custom_prompts
)

result3 = agent3.run("计算 (25 + 15) * 3 - 8 的结果")
print(f"\n🎯 最终结果: {result3}")

# ==================== 测试4：Planner 类独立测试 ====================
print("\n" + "="*80)
print("测试4：Planner 类独立测试")
print("="*80)

planner = Planner(llm)

print("\n--- 测试基础规划 ---")
plan1 = planner.plan("制定一个学习Python的三个月计划")
print(f"计划步骤数: {len(plan1)}")
for i, step in enumerate(plan1, 1):
    print(f"{i}. {step}")

print("\n--- 测试数学问题规划 ---")
plan2 = planner.plan("鸡兔同笼问题：有35个头，94只脚，问鸡兔各几只？")
print(f"计划步骤数: {len(plan2)}")
for i, step in enumerate(plan2, 1):
    print(f"{i}. {step}")

# ==================== 测试5：Executor 类独立测试 ====================
print("\n" + "="*80)
print("测试5：Executor 类独立测试")
print("="*80)

executor = Executor(llm)

# 创建一个测试计划
test_plan = [
    "解释什么是面向对象编程",
    "列举面向对象的三大特性",
    "为每个特性提供简要说明"
]

print("\n--- 执行测试计划 ---")
result5 = executor.execute("解释面向对象编程", test_plan)
print(f"\n最终结果长度: {len(result5)} 字符")

# ==================== 测试6：多任务连续处理 ====================
print("\n" + "="*80)
print("测试6：多任务连续处理")
print("="*80)

multi_task_agent = PlanAndSolveAgent(
    name="多任务规划助手",
    llm=llm
)

# 任务1
print("\n--- 任务1 ---")
result6a = multi_task_agent.run("解释什么是快速排序算法")
print(f"结果1长度: {len(result6a)} 字符")

# 任务2（独立的任务）
print("\n--- 任务2 ---")
result6b = multi_task_agent.run("解释什么是归并排序算法")
print(f"结果2长度: {len(result6b)} 字符")

print(f"\n总对话历史: {len(multi_task_agent.get_history())} 条消息")

# ==================== 测试7：复杂问题分解 ====================
print("\n" + "="*80)
print("测试7：复杂问题分解")
print("="*80)

agent7 = PlanAndSolveAgent(
    name="复杂问题助手",
    llm=llm
)

complex_question = """
请设计一个完整的图书管理系统，要求：
1. 可以添加、删除、查询图书
2. 可以借阅和归还图书
3. 可以管理读者信息
4. 请提供系统架构设计
"""

result7 = agent7.run(complex_question)
print(f"\n最终结果长度: {len(result7)} 字符")

# ==================== 测试8：计划为空的情况 ====================
print("\n" + "="*80)
print("测试8：计划为空的情况")
print("="*80)

agent8 = PlanAndSolveAgent(
    name="边界测试助手",
    llm=llm
)

# 使用一个可能导致计划失败的问题（或者LLM返回格式错误）
result8 = agent8.run("你好")
print(f"\n结果: {result8[:200] if result8 else '无响应'}...")

# ==================== 测试9：清空历史测试 ====================
print("\n" + "="*80)
print("测试9：清空历史测试")
print("="*80)

agent9 = PlanAndSolveAgent(
    name="可清空助手",
    llm=llm
)

# 执行任务
agent9.run("任务1：介绍Python")
print(f"\n清空前 - 对话历史: {len(agent9.get_history())} 条")

# 清空历史
agent9.clear_history()
print(f"清空后 - 对话历史: {len(agent9.get_history())} 条")

# 执行新任务
agent9.run("任务2：介绍JavaScript")
print(f"新任务后 - 对话历史: {len(agent9.get_history())} 条")

# ==================== 测试10：并行多个独立 Agent ====================
print("\n" + "="*80)
print("测试10：并行多个独立 PlanAndSolveAgent")
print("="*80)

agent_a = PlanAndSolveAgent(name="助手A", llm=llm)
agent_b = PlanAndSolveAgent(name="助手B", llm=llm)
agent_c = PlanAndSolveAgent(name="助手C", llm=llm)

question = "什么是人工智能？"

print("\n--- 助手A ---")
result_a = agent_a.run(question)
print(f"结果: {result_a[:150]}...")

print("\n--- 助手B ---")
result_b = agent_b.run(question)
print(f"结果: {result_b[:150]}...")

print("\n--- 助手C ---")
result_c = agent_c.run(question)
print(f"结果: {result_c[:150]}...")

# 验证独立性
print(f"\n助手A历史: {len(agent_a.get_history())} 条")
print(f"助手B历史: {len(agent_b.get_history())} 条")
print(f"助手C历史: {len(agent_c.get_history())} 条")

# ==================== 测试11：DEFAULT_PROMPTS 测试 ====================
print("\n" + "="*80)
print("测试11：默认提示词模板测试")
print("="*80)

print("\n--- DEFAULT_PLANNER_PROMPT 预览 ---")
print(DEFAULT_PLANNER_PROMPT[:200] + "...")

print("\n--- DEFAULT_EXECUTOR_PROMPT 预览 ---")
print(DEFAULT_EXECUTOR_PROMPT[:200] + "...")

print("\n--- 模板变量 ---")
print("Planner变量: {question}")
print("Executor变量: {question}, {plan}, {history}, {current_step}")

# ==================== 测试12：自定义 Planner 提示词 ====================
print("\n" + "="*80)
print("测试12：自定义 Planner 提示词")
print("="*80)

custom_planner_prompt = """
你是一位项目管理专家。请将以下项目分解为可执行的任务列表。

项目: {question}

请输出格式：
```python
["任务1", "任务2", "任务3"]
```
"""

planner_custom = Planner(llm, custom_planner_prompt)
plan12 = planner_custom.plan("开发一个简单的个人博客网站")

print(f"\n计划步骤数: {len(plan12)}")
for i, step in enumerate(plan12, 1):
    print(f"{i}. {step}")

# ==================== 测试13：自定义 Executor 提示词 ====================
print("\n" + "="*80)
print("测试13：自定义 Executor 提示词")
print("="*80)

custom_executor_prompt = """
你是代码编写专家。请根据当前步骤编写代码。

问题: {question}
计划: {plan}
历史: {history}
当前步骤: {current_step}

请提供完整的代码实现:
"""

executor_custom = Executor(llm, custom_executor_prompt)
test_plan_13 = ["编写计算两个数之和的函数", "编写计算两个数之积的函数"]

result13 = executor_custom.execute("编写基础数学函数", test_plan_13)
print(f"\n最终结果长度: {len(result13)} 字符")

# ==================== 测试14：Planner 和 Executor 组合测试 ====================
print("\n" + "="*80)
print("测试14：Planner 和 Executor 组合测试")
print("="*80)

planner14 = Planner(llm)
executor14 = Executor(llm)

question14 = "解释什么是深度学习，以及它与机器学习的区别"

print("\n--- 规划阶段 ---")
plan14 = planner14.plan(question14)
print(f"计划生成: {len(plan14)} 个步骤")

print("\n--- 执行阶段 ---")
result14 = executor14.execute(question14, plan14)
print(f"\n最终结果长度: {len(result14)} 字符")

# ==================== 测试15：边界情况测试 ====================
print("\n" + "="*80)
print("测试15：边界情况测试")
print("="*80)

agent15 = PlanAndSolveAgent(
    name="边界测试助手",
    llm=llm
)

# 15.1 空字符串
print("\n--- 15.1 空字符串 ---")
try:
    result15a = agent15.run("")
    print(f"结果: {result15a[:100] if result15a else '无响应'}...")
except Exception as e:
    print(f"错误: {e}")

# 15.2 极短问题
print("\n--- 15.2 极短问题 ---")
try:
    result15b = agent15.run("Hi")
    print(f"结果: {result15b[:100] if result15b else '无响应'}...")
except Exception as e:
    print(f"错误: {e}")

# 15.3 多行问题
print("\n--- 15.3 多行问题 ---")
try:
    result15c = agent15.run("""
    任务1
    任务2
    任务3
    """)
    print(f"结果: {result15c[:100] if result15c else '无响应'}...")
except Exception as e:
    print(f"错误: {e}")

# ==================== 总结统计 ====================
print("\n" + "="*80)
print("测试总结")
print("="*80)

print("\n✅ 所有测试完成！")
print("\n测试覆盖:")
print("  1. 基础 PlanAndSolveAgent（默认配置）")
print("  2. 数学问题求解")
print("  3. 自定义提示词模板")
print("  4. Planner 类独立测试")
print("  5. Executor 类独立测试")
print("  6. 多任务连续处理")
print("  7. 复杂问题分解")
print("  8. 计划为空的情况")
print("  9. 清空历史测试")
print("  10. 并行多个独立 Agent")
print("  11. DEFAULT_PROMPTS 测试")
print("  12. 自定义 Planner 提示词")
print("  13. 自定义 Executor 提示词")
print("  14. Planner 和 Executor 组合测试")
print("  15. 边界情况测试")

print("\n" + "="*80)
