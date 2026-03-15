"""测试后端 Agent 是否正常工作"""

import asyncio
import sys
import os
sys.path.insert(0, '/Users/kenshin/Projects/my-agents/helloagents-trip-planner/backend')

from app.agents.trip_planner_agent import get_trip_planner_agent
from app.models.schemas import TripRequest

async def test_agent():
    print("=" * 60)
    print("测试后端 Agent 和工具")
    print("=" * 60)

    try:
        # 获取 Agent 实例
        print("\n1️⃣ 初始化 Agent...")
        agent = get_trip_planner_agent()

        # 检查工具
        print("\n2️⃣ 检查工具列表...")
        tools = agent.attraction_agent.list_tools()
        print(f"   景点搜索 Agent 工具数量: {len(tools)}")
        print("   工具列表:")
        for tool in tools:
            print(f"      - {tool}")

        # 测试简单请求
        print("\n3️⃣ 测试简单请求...")
        request = TripRequest(
            city="北京",
            start_date="2025-03-10",
            end_date="2025-03-10",
            travel_days=1,
            transportation="公共交通",
            accommodation="经济型酒店",
            preferences=[],
            free_text_input=""
        )

        print("   开始生成旅行计划...")
        result = agent.plan_trip(request)
        print(f"\n   结果: {result.city if result else '失败'}")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())
