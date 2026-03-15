"""测试参数类型修复是否有效"""

import asyncio
import os
import sys
import json

# 确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

async def test_mcp_direct():
    """直接测试MCP服务器的参数处理"""
    print("=" * 60)
    print("测试 MCP 服务器参数类型处理")
    print("=" * 60)

    # 导入MCP工具
    from tiny_agents.tools import MCPTool

    api_key = os.getenv("AMAP_API_KEY")
    if not api_key:
        print("❌ AMAP_API_KEY 未设置")
        return

    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")

    # 创建MCP工具
    print("\n1️⃣ 创建 MCP 工具...")
    amap_tool = MCPTool(
        name="amap",
        description="高德地图服务",
        server_command=["python", "-m", "app.services.amap_mcp_server"],
        env={"AMAP_API_KEY": api_key},
        auto_expand=False
    )

    def parse_mcp_result(result):
        """解析MCP工具返回的结果"""
        if not isinstance(result, str):
            return result

        # 尝试找到JSON内容
        if '{' in result:
            start = result.find('{')
            # 找到匹配的结束位置
            end = result.rfind('}') + 1
            result = result[start:end]
        elif '[]' in result:
            # 处理空数组情况
            return '{"pois": []}'

        return result

    # 测试2: 使用字符串 "true" - 添加调试信息
    print("\n2️⃣ 测试: 使用字符串 'true' (带调试)")
    try:
        result = amap_tool.run({
            "action": "call_tool",
            "tool_name": "maps_text_search",
            "arguments": {
                "keywords": "美食",
                "city": "北京",
                "citylimit": "true"
            }
        })
        print(f"   原始响应: {repr(result[:200])}")
        result = parse_mcp_result(result)
        print(f"   解析后: {repr(result[:200])}")
        data = json.loads(result)
        if data.get("status") == "1":
            print("   ✅ 字符串 'true' 测试成功")
            pois = data.get("pois", [])
            print(f"   找到 {len(pois)} 个POI")
        else:
            print(f"   ❌ 字符串 'true' 测试失败: {data.get('info', '未知错误')}")
    except Exception as e:
        print(f"   ❌ 字符串 'true' 测试异常: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_mcp_direct())
