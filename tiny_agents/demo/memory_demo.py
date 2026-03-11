

from tiny_agents.tools.builtin.memory_tool import MemoryTool
from tiny_agents.agents.simple_agent import SimpleAgent
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.tools.registry import ToolRegistry

llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="Memory Agent",
    llm=llm,
    system_prompt="你是一个拥有记忆能力的AI助手." 
)

memory_tool = MemoryTool(user_id="user123")
tool_registry = ToolRegistry()
tool_registry.register_tool(memory_tool)
agent.tool_registry = tool_registry

print("第一次对话:")
result = memory_tool.execute(
    action="add", 
    content="我的名字是山河剑心，是一名人工智能爱好者，专注于LLM和AI相关技术。 我喜欢学习和分享人工智能的最新发展。",
    memory_type="semantic",
    importance=0.8
)
print("Agent Response:", result)


print("第二次对话:")
result2 = memory_tool.execute(
    action="add", 
    content="我的名字是秋叶悲歌，是一名内容创作者，专注于短视频制作。 我喜欢分享最新的短视频制作技巧和经验。",
    memory_type="semantic",
    importance=0.7
)
print("Agent Response:", result2)

print("第三次对话:")
result3 = memory_tool.execute(
    action="add", 
    content="我的名字是春华秋实，是一名产品经理，专注于产品设计和用户体验。",
    memory_type="semantic",
    importance=0.6
)
print("Agent Response:", result3)

print("\n=== 搜索特定记忆 ===")
# 搜索前端相关的记忆
print("🔍 搜索 '人工智能':")
result = memory_tool.execute("query_points", query="人工智能", limit=3, user_id="user123")
print(result)
print("\n=== 记忆摘要 ===")
result = memory_tool.execute("summary")
print(result)   