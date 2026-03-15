"""测试 MCP 工具是否正常工作"""

import asyncio
import os
import json
from hello_agents.tools import MCPTool

async def test_mcp_tool():
    """测试 MCP 工具"""
    print("=" * 60)
    print("测试 MCP 工具 - amap-mcp-server")
    print("=" * 60)

    # 获取 API key
    api_key = os.getenv("AMAP_API_KEY", "8b77c01f5af0af2bdb86f6d42568fedb")
    print(f"🔑 使用 API Key: {api_key[:10]}...{api_key[-4:]}")

    # 创建 MCP 工具
    print("\n1️⃣ 创建 MCP 工具...")
    amap_tool = MCPTool(
        name="amap",
        description="高德地图服务",
        server_command=["uvx", "amap-mcp-server"],
        env={"AMAP_MAPS_API_KEY": api_key},
        auto_expand=True
    )

    # 测试工具调用 - 列出所有可用工具
    print("\n2️⃣ 列出所有可用工具...")
    result = amap_tool.run({"action": "list_tools"})
    print(f"返回类型: {type(result)}")
    print(f"返回内容: {result}")

    # 打印内部工具列表
    print(f"\n3️⃣ 内部工具列表:")
    print(f"可用工具: {amap_tool._available_tools}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_mcp_tool())
