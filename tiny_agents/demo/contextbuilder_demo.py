from tiny_agents.context.builder import ContextBuilder, ContextConfig
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.tools.builtin import MemoryTool, RAGTool
from tiny_agents.agents import SimpleAgent
from tiny_agents.tools.registry import ToolRegistry

class ContextAwareAgent(SimpleAgent):
    """
    上下文感知智能体 - 结合记忆工具和 RAG 工具的简单智能体
    """
    def __init__(self, name: str, llm: HelloAgentsLLM, **kwargs):
        super().__init__(name=name, llm=llm, system_prompt=kwargs.get("system_prompt", ""))
        self.memory_tool = MemoryTool(user_id=kwargs.get("user_id", "default"))
        self.rag_tool = RAGTool(knowledge_base_path=kwargs.get("knowledge_base_path", "./kb"))
        self.context_builder = ContextBuilder(
            memory_tool=self.memory_tool,
            rag_tool=self.rag_tool,
            config=ContextConfig(max_tokens=kwargs.get("max_tokens", 4096))
        )

        self.conversation_history = []

    def run(self, user_query, **kwargs) -> str:
        """
        运行智能体，处理输入文本并返回输出
        
        """
        optimized_context = self.context_builder.build(
            user_query=user_query,
            conversation_history=self.conversation_history,
            system_instructions=self.system_prompt
        )

        messages = [
            {"role": "system", "content": optimized_context},
            {"role": "user", "content": user_query}
        ]
        response = self.llm.invoke(messages)

        # 3. 更新对话历史
        from tiny_agents.core.message import Message
        from datetime import datetime
        self.conversation_history.append(
            Message(content=user_query, role="user", timestamp=datetime.now())
        )

        self.conversation_history.append(
            Message(content=response, role="assistant", timestamp=datetime.now())
        )

        # 4. 将重要交互记录到记忆系统
        self.memory_tool.run({
            "action": "add",
            "content": f"Q: {user_query}\nA: {response}...", # 摘要
            "memory_type": "episodic",
            "importance": 0.6
        })

        return response


if __name__ == "__main__":
    llm = HelloAgentsLLM()
    agent = ContextAwareAgent(
        name="数据分析顾问",
        llm=llm,
        system_prompt="你是一位资深的Python数据工程顾问。",
        user_id="user123",
        knowledge_base_path="./data_science_kb"
    )

    response = agent.run("如何优化Pandas的内存占用？")
    print("智能体回复：", response)