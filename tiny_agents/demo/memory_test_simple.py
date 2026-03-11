"""简单的记忆测试脚本 - 仅使用 SQLite 存储，不依赖 Qdrant"""

from tiny_agents.agents.simple_agent import SimpleAgent
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.tools.builtin.memory_tool import MemoryTool
from tiny_agents.tools.registry import ToolRegistry
import os

# 禁用 Qdrant，使用本地存储
os.environ.pop('QDRANT_URL', None)
os.environ.pop('QDRANT_API_KEY', None)

llm = HelloAgentsLLM()
tool_registry = ToolRegistry()

agent = SimpleAgent(
    name="Memory Agent",
    llm=llm,
    system_prompt="你是一个拥有记忆能力的AI助手。"
)

# 创建记忆工具（会自动 fallback 到 SQLite 存储）
memory_tool = MemoryTool(user_id="test_user")
tool_registry.register_tool(memory_tool)

agent.tool_registry = tool_registry

# 测试对话
print("=== 测试对话 1 ===")
response1 = agent.run("你好！我叫山河剑心，我喜欢人工智能。")
print(f"Agent: {response1}")

print("\n=== 测试对话 2 ===")
response2 = agent.run("记住我叫什么名字了吗？")
print(f"Agent: {response2}")

print("\n=== 测试对话 3 ===")
response3 = agent.run("我喜欢什么话题？")
print(f"Agent: {response3}")

print("\n✓ 测试完成！")
