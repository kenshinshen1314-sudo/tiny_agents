# test_simple_agent_v2.py
"""SimpleAgent 测试脚本 v2 - 直接测试核心 SimpleAgent 类"""

from dotenv import load_dotenv
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.core.message import Message
from tiny_agents.agents.simple_agent import SimpleAgent

# 加载环境变量
load_dotenv()

# 创建LLM实例
llm = HelloAgentsLLM()

# ==================== 测试1：基础 SimpleAgent（无系统提示词） ====================
print("\n" + "="*80)
print("测试1：基础 SimpleAgent（无系统提示词）")
print("="*80)

basic_agent = SimpleAgent(
    name="基础助手",
    llm=llm
)

response1 = basic_agent.run("你好，请介绍一下自己")
print(f"\n🎯 响应: {response1}")
print(f"📝 对话历史: {len(basic_agent.get_history())} 条消息")

# ==================== 测试2：带系统提示词的 SimpleAgent ====================
print("\n" + "="*80)
print("测试2：带系统提示词的 SimpleAgent")
print("="*80)

agent_with_prompt = SimpleAgent(
    name="专业助手",
    llm=llm,
    system_prompt="你是一位专业的Python编程导师。你的回答应该简洁、准确，并包含代码示例。"
)

response2 = agent_with_prompt.run("请解释Python中的列表推导式")
print(f"\n🎯 响应: {response2}")

# ==================== 测试3：多轮对话测试 ====================
print("\n" + "="*80)
print("测试3：多轮对话测试")
print("="*80)

conversation_agent = SimpleAgent(
    name="对话助手",
    llm=llm,
    system_prompt="你是一个友好的AI助手，擅长进行连续对话。"
)

# 第一轮
print("\n--- 第一轮对话 ---")
response3a = conversation_agent.run("我想学习Python编程，应该从哪里开始？")
print(f"用户: 我想学习Python编程，应该从哪里开始？")
print(f"助手: {response3a}")

# 第二轮（依赖上一轮的上下文）
print("\n--- 第二轮对话 ---")
response3b = conversation_agent.run("能给我推荐一些学习资源吗？")
print(f"用户: 能给我推荐一些学习资源吗？")
print(f"助手: {response3b}")

# 第三轮（继续上下文）
print("\n--- 第三轮对话 ---")
response3c = conversation_agent.run("大概需要多长时间能掌握基础？")
print(f"用户: 大概需要多长时间能掌握基础？")
print(f"助手: {response3c}")

print(f"\n📝 总对话历史: {len(conversation_agent.get_history())} 条消息")

# ==================== 测试4：流式响应测试 ====================
print("\n" + "="*80)
print("测试4：流式响应测试")
print("="*80)

stream_agent = SimpleAgent(
    name="流式助手",
    llm=llm,
    system_prompt="你是一位知识渊博的科普专家。"
)

print("\n🌊 开始流式输出:")
print("-" * 60)
full_response = ""
for chunk in stream_agent.stream_run("请用通俗易懂的语言解释什么是机器学习"):
    full_response += chunk
print("-" * 60)
print(f"\n✅ 流式输出完成，总长度: {len(full_response)} 字符")

# ==================== 测试5：历史记录管理测试 ====================
print("\n" + "="*80)
print("测试5：历史记录管理测试")
print("="*80)

history_agent = SimpleAgent(
    name="历史测试助手",
    llm=llm,
    system_prompt="你是一个有记忆力的助手。"
)

# 进行多轮对话
history_agent.run("我的名字是张三")
history_agent.run("我今年25岁")
history_agent.run("我喜欢阅读科幻小说")

# 查看历史记录
print("\n📝 对话历史记录:")
history = history_agent.get_history()
for i, msg in enumerate(history, 1):
    role_emoji = "👤" if msg.role == "user" else "🤖"
    content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
    print(f"  {i}. {role_emoji} [{msg.role}]: {content_preview}")

# 测试记忆是否有效
print("\n--- 测试上下文记忆 ---")
memory_test_response = history_agent.run("你还记得我叫什么名字吗？我今年多大？")
print(f"助手: {memory_test_response}")

# ==================== 测试6：清空历史测试 ====================
print("\n" + "="*80)
print("测试6：清空历史测试")
print("="*80)

clear_agent = SimpleAgent(
    name="清空历史助手",
    llm=llm
)

clear_agent.run("我说过我喜欢编程")
print(f"\n清空前 - 历史记录数: {len(clear_agent.get_history())}")

clear_agent.clear_history()
print(f"清空后 - 历史记录数: {len(clear_agent.get_history())}")

# 验证清空后的对话没有上下文
print("\n--- 测试清空后的对话 ---")
clear_response = clear_agent.run("我刚才说我喜欢什么？")
print(f"助手: {clear_response}")
print("(应该无法回答，因为历史已清空)")

# ==================== 测试7：不同角色/系统提示词对比 ====================
print("\n" + "="*80)
print("测试7：不同角色/系统提示词对比")
print("="*80)

test_question = "什么是递归？"

# 7.1 通用助手
general_agent = SimpleAgent(
    name="通用助手",
    llm=llm,
    system_prompt="你是一个通用的AI助手，用简单易懂的语言回答问题。"
)

print("\n--- 7.1 通用助手 ---")
response7a = general_agent.run(test_question)
print(f"响应: {response7a[:200]}...")

# 7.2 技术专家
tech_agent = SimpleAgent(
    name="技术专家",
    llm=llm,
    system_prompt="你是一位资深的软件工程师和技术专家，你的回答应该专业、深入，并包含技术细节和代码示例。"
)

print("\n--- 7.2 技术专家 ---")
response7b = tech_agent.run(test_question)
print(f"响应: {response7b[:200]}...")

# 7.3 教师
teacher_agent = SimpleAgent(
    name="教师",
    llm=llm,
    system_prompt="你是一位有耐心的教师，擅长用比喻和实例来讲解复杂的概念。你的回答应该适合初学者理解。"
)

print("\n--- 7.3 教师 ---")
response7c = teacher_agent.run(test_question)
print(f"响应: {response7c[:200]}...")

# ==================== 测试8：长对话处理测试 ====================
print("\n" + "="*80)
print("测试8：长对话处理测试")
print("="*80)

long_conversation_agent = SimpleAgent(
    name="长对话助手",
    llm=llm,
    system_prompt="你是一个专业的知识问答助手。"
)

long_question = """
请详细解释以下概念：
1. 什么是面向对象编程（OOP）？
2. OOP的三大核心特性是什么？
3. 请为每个特性提供具体的代码示例。
4. OOP相比面向过程编程有什么优势？
"""

print("\n--- 长对话测试 ---")
response8 = long_conversation_agent.run(long_question)
print(f"响应长度: {len(response8)} 字符")
print(f"响应预览: {response8[:300]}...")

# ==================== 测试9：特殊字符和边界情况测试 ====================
print("\n" + "="*80)
print("测试9：特殊字符和边界情况测试")
print("="*80)

boundary_agent = SimpleAgent(
    name="边界测试助手",
    llm=llm
)

# 9.1 空字符串
print("\n--- 9.1 空字符串 ---")
try:
    response9a = boundary_agent.run("")
    print(f"空字符串响应: {response9a[:100] if response9a else '无响应'}")
except Exception as e:
    print(f"错误: {e}")

# 9.2 特殊字符
print("\n--- 9.2 特殊字符 ---")
response9b = boundary_agent.run("请解释以下符号的含义：@, #, $, %, &, *, ~, ^")
print(f"响应: {response9b[:200]}...")

# 9.3 多语言混合
print("\n--- 9.3 多语言混合 ---")
response9c = boundary_agent.run("Please explain what 'Hello World' means in programming: 用中文回答")
print(f"响应: {response9c[:200]}...")

# ==================== 测试10：并行创建多个 Agent ====================
print("\n" + "="*80)
print("测试10：并行创建多个独立 Agent")
print("="*80)

# 创建多个独立的 Agent，每个有独立的上下文
agent_a = SimpleAgent(name="助手A", llm=llm, system_prompt="你是一个英语助手，只说英语。")
agent_b = SimpleAgent(name="助手B", llm=llm, system_prompt="你是一个中文助手，只说中文。")
agent_c = SimpleAgent(name="助手C", llm=llm, system_prompt="你是一个日语助手，只说日语。")

question = "你好"

print("\n--- 助手A（英语）---")
response10a = agent_a.run(question)
print(f"响应: {response10a}")

print("\n--- 助手B（中文）---")
response10b = agent_b.run(question)
print(f"响应: {response10b}")

print("\n--- 助手C（日语）---")
response10c = agent_c.run(question)
print(f"响应: {response10c}")

# 验证独立性
print("\n--- 验证 Agent 独立性 ---")
print(f"助手A历史: {len(agent_a.get_history())} 条")
print(f"助手B历史: {len(agent_b.get_history())} 条")
print(f"助手C历史: {len(agent_c.get_history())} 条")

# ==================== 总结统计 ====================
print("\n" + "="*80)
print("测试总结")
print("="*80)

print("\n✅ 所有测试完成！")
print("\n测试覆盖:")
print("  1. 基础 SimpleAgent（无系统提示词）")
print("  2. 带系统提示词的 SimpleAgent")
print("  3. 多轮对话测试")
print("  4. 流式响应测试")
print("  5. 历史记录管理测试")
print("  6. 清空历史测试")
print("  7. 不同角色/系统提示词对比")
print("  8. 长对话处理测试")
print("  9. 特殊字符和边界情况测试")
print("  10. 并行创建多个独立 Agent")

print("\n" + "="*80)
