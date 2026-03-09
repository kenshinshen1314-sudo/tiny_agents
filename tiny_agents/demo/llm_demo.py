from dotenv import load_dotenv
from tiny_agents.core.llm import HelloAgentsLLM

load_dotenv()  # 加载环境变量

if __name__ == "__main__":
    # 初始化LLM客户端
    llm_client = HelloAgentsLLM()  # 替换为你选择的提供商

    # 测试LLM响应
    messages = [{"role": "user", "content": "请介绍一下自己。"}]
    response = llm_client.think(messages=messages)
    print("LLM响应:", response)

    for chunk in llm_client.think(messages=messages):
        print(chunk, end="")

