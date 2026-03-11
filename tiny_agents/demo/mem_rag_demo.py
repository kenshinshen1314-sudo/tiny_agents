from tiny_agents.tools.builtin.rag_tool import RAGTool
from tiny_agents.agents.simple_agent import SimpleAgent 
from tiny_agents.tools.builtin.memory_tool import MemoryTool
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.tools.registry import ToolRegistry


llm = HelloAgentsLLM()
tool_registry = ToolRegistry()

agent = SimpleAgent(
    name="RAG&MEM Agent",
    llm=llm,
    system_prompt="你是一个拥有记忆和知识检索能力的AI助手." 
)

memory_tool = MemoryTool(user_id="user123")
tool_registry.register_tool(memory_tool)

rag_tool = RAGTool(knowledge_base_path="./knowledge_base.json")
tool_registry.register_tool(rag_tool)

agent.tool_registry = tool_registry

response = agent.run("你好！请记住我叫山河剑心。请告诉我关于人工智能的最新信息，并记住我喜欢这个话题。")
print("Agent Response:", response)
