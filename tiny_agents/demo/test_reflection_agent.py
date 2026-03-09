# test_reflection_agent.py
"""Reflection Agent 测试脚本"""

from dotenv import load_dotenv
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.demo.my_reflection_agent import (
    MyReflectionAgent,
    create_agent
)

# 加载环境变量
load_dotenv()

# 创建LLM实例
llm = HelloAgentsLLM()

# ==================== 测试1：通用Reflection Agent ====================
print("\n" + "="*80)
print("测试1：通用Reflection Agent")
print("="*80)
general_agent = MyReflectionAgent(
    name="通用反思助手",
    llm=llm,
    domain="general",
    max_iterations=3
)
result1 = general_agent.run("用Python实现一个简单的计算器，支持加减乘除运算")
print(f"\n🎯 最终结果已获取")

# ==================== 测试2：代码领域Agent ====================
print("\n" + "="*80)
print("测试2：代码领域Reflection Agent")
print("="*80)
coding_agent = create_agent(
    name="代码审查专家",
    llm=llm,
    domain="coding",
    max_iterations=3
)
result2 = coding_agent.run("编写一个Python函数，实现快速排序算法")
print(f"\n🎯 最终结果已获取")

# ==================== 测试3：写作领域Agent ====================
print("\n" + "="*80)
print("测试3：写作领域Reflection Agent")
print("="*80)
writing_agent = create_agent(
    name="内容编辑专家",
    llm=llm,
    domain="writing",
    max_iterations=3
)
result3 = writing_agent.run("写一篇关于人工智能未来发展的短文，约200字")
print(f"\n🎯 最终结果已获取")

# ==================== 测试4：分析领域Agent ====================
print("\n" + "="*80)
print("测试4：分析领域Reflection Agent")
print("="*80)
analysis_agent = create_agent(
    name="数据分析专家",
    llm=llm,
    domain="analysis",
    max_iterations=3
)
result4 = analysis_agent.run("分析远程办公对员工生产力的影响")
print(f"\n🎯 最终结果已获取")

# ==================== 测试5：查看统计信息 ====================
print("\n" + "="*80)
print("测试5：查看执行统计")
print("="*80)

print(f"\n📊 代码领域Agent统计:")
stats = coding_agent.get_stats()
print(f"  - 总迭代轮数: {stats['total_iterations']}")
print(f"  - 优化次数: {stats['improvements_made']}")
print(f"  - 反馈条目: {len(stats['feedback_items'])}")

print(f"\n📝 写作领域Agent记忆记录:")
records = writing_agent.get_memory_records()
print(f"  - 总记录数: {len(records)}")
for i, record in enumerate(records, 1):
    print(f"  - 记录{i}: {record['type']} ({len(record['content'])} 字符)")

# ==================== 测试6：流式运行 ====================
print("\n" + "="*80)
print("测试6：流式运行")
print("="*80)

stream_agent = MyReflectionAgent(
    name="流式反思助手",
    llm=llm,
    domain="general",
    max_iterations=1
)

print("\n🌊 开始流式输出:")
for chunk in stream_agent.stream_run("解释什么是递归"):
    print(chunk, end="", flush=True)

print("\n" + "="*80)
print("✅ 所有测试完成")
print("="*80)