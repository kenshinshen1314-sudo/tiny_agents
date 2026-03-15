"""多智能体旅行规划系统"""

import json
import math
import re
from typing import Dict, Any, List, Optional, Callable
from tiny_agents.agents import SimpleAgent
from tiny_agents.tools import MCPTool
from ..services.llm_service import get_llm
from ..models.schemas import TripRequest, TripPlan, DayPlan, Attraction, Meal, WeatherInfo, Location, Hotel
from ..config import get_settings

# ============ 进度回调 ============

class ProgressCallback:
    """进度回调类，用于实时推送进度"""

    STEPS = [
        {"step": 1, "title": "🔍 搜索景点", "message": "正在搜索相关景点...", "progress": 10},
        {"step": 2, "title": "🍽️ 搜索美食", "message": "正在搜索当地美食...", "progress": 25},
        {"step": 3, "title": "🌤️ 查询天气", "message": "正在查询目的地的天气情况...", "progress": 40},
        {"step": 4, "title": "🏨 推荐酒店", "message": "正在搜索合适的酒店...", "progress": 55},
        {"step": 5, "title": "📋 生成行程", "message": "正在生成详细的旅行计划...", "progress": 75},
        {"step": 6, "title": "🚗 计算路线", "message": "正在计算每天的交通路线...", "progress": 90},
    ]

    def __init__(self):
        self._step = 0
        self._progress = 0
        self._message = "准备中..."
        self._callback: Optional[Callable] = None

    def set_callback(self, callback: Callable):
        """设置回调函数"""
        self._callback = callback

    def update(self, step: int, message: str = "", progress: int = 0):
        """更新进度"""
        if step > 0 and step <= len(self.STEPS):
            step_info = self.STEPS[step - 1]
            self._step = step
            self._progress = step_info["progress"]
            self._message = step_info["message"]
        else:
            self._step = step
            self._progress = progress
            if message:
                self._message = message

        if self._callback:
            self._callback(self.get_progress())

    def get_progress(self) -> Dict[str, Any]:
        """获取当前进度"""
        return {
            "step": self._step,
            "progress": self._progress,
            "message": self._message,
            "status": "running"
        }
    
# ============ Agent提示词 ============

ATTRACTION_AGENT_PROMPT = """你是景点搜索专家。你的任务是根据城市和用户偏好搜索合适的景点。

**工作流程:**
1. 接收用户的搜索请求
2. 使用 amap_maps_text_search 工具搜索景点
3. 从搜索结果中提取关键信息（景点名称、地址、经纬度、评分等）
4. 整理成用户友好的格式返回

**工具使用:**
- 工具名称: amap_maps_text_search
- 参数: keywords (搜索关键词), city (城市名), citylimit (是否限制在城市范围)

**示例:**
用户: "搜索北京的历史文化景点"
你的处理:
- 使用工具搜索: keywords="历史文化", city="北京"
- 从结果中提取: 故宫、天坛、颐和园等
- 返回格式化的列表给用户

**工具结果判断:**
- 如果工具返回结果中包含 "✅ 搜索成功" 或 "status": "1"，说明调用成功
- 如果工具返回结果中包含 "❌" 或 "status": "0"，说明调用失败
- 成功时从 JSON 数据中提取真实景点信息
- 失败时返回空数组 []

**输出要求:**
- 列出3-5个最相关的景点
- 包含: 景点名称、地址、评分、简要描述
- 不要编造数据,工具返回什么就返回什么
- 必须返回符合 JSON 格式的数组:
**输出示例:**
[
    {
      "name": "橘子洲风景名胜区",
      "address": "橘子洲头2号",
      "location": {"longitude": 112.963081, "latitude": 28.196505},
      "rating": 4.9,
      "description": "长沙地标性景点，湘江江心洲，风景秀丽，适合休闲散步和观赏烟花",
      "category": "风景名胜",
      "visit_duration": 180,
      "ticket_price": 0
    },
    {
      "name": "岳麓山风景名胜区",
      "address": "登高路58号",
      "location": {"longitude": 112.936104, "latitude": 28.183601},
      "rating": 4.8,
      "description": "国家5A级景区，自然风光与历史文化完美融合，登高望远的好去处",
      "category": "自然风光",
      "visit_duration": 240,
      "ticket_price": 0
    }
]
"""

GOURMET_FOOD_AGENT_PROMPT = """你是美食搜索专家。你的任务是根据城市和用户口味偏好、就餐环境偏好搜索合适的餐厅。

**工作流程:**
1. 接收用户的搜索请求
2. 使用 amap_maps_text_search 工具搜索餐厅
3. 从搜索结果中提取关键信息（餐厅名称、地址、经纬度、评分等）
4. 整理成用户友好的格式返回

**工具使用:**
- 工具名称: amap_maps_text_search
- 参数: keywords (搜索关键词), city (城市名), citylimit (是否限制在城市范围)

**示例:**
用户: "搜索北京的美食"
你的处理:
- 使用工具搜索: keywords="美食", city="北京"
- 从结果中提取: 北京美食、北京餐厅等
- 返回格式化的列表给用户

**输出要求:**
- 列出10个最相关的餐厅、美食、餐馆
- 包含: 餐厅名称、地址、评分、简要描述
- 不要编造数据,工具返回什么就返回什么
- 必须返回符合 JSON 格式的数组:
**输出示例:**
[
{
    "type": "breakfast",
    "name": "餐厅名称",
    "address": "详细地址",
    "location": {"longitude": 经度, "latitude": 纬度},
    "description": "特色菜品或餐厅描述（包含2-3个招牌菜）",
    "estimated_cost": 人均消费（元，根据餐厅档次估算：小吃街20-50元，普通餐-厅50-100元，特色餐厅100-200元）
},
{
    "type": "lunch",
    "name": "餐厅名称",
    "address": "详细地址",
    "location": {"longitude": 经度, "latitude": 纬度},
    "description": "特色菜品或餐厅描述（包含2-3个招牌菜）",
    "estimated_cost": 人均消费（元，根据餐厅档次估算：小吃街20-50元，普通餐-厅50-100元，特色餐厅100-200元）
},
{
    "type": "dinner",
    "name": "餐厅名称",
    "address": "详细地址",
    "location": {"longitude": 经度, "latitude": 纬度},
    "description": "特色菜品或餐厅描述（包含2-3个招牌菜）",
    "estimated_cost": 人均消费（元，根据餐厅档次估算：小吃街20-50元，普通餐-厅50-100元，特色餐厅100-200元）
},
{
    "type": "snack",
    "name": "餐厅名称",
    "address": "详细地址",
    "location": {"longitude": 经度, "latitude": 纬度},
    "description": "特色菜品或餐厅描述（包含2-3个招牌菜）",
    "estimated_cost": 人均消费（元，根据餐厅档次估算：小吃街20-50元，普通餐-厅50-100元，特色餐厅100-200元）
}
]

"""




WEATHER_AGENT_PROMPT = """你是天气查询专家。你的任务是查询指定城市的天气信息。

**工作流程:**
1. 接收城市名
2. 使用 amap_maps_weather 工具查询天气
3. 解析返回的天气数据
4. 按照 WeatherInfo 格式输出 JSON

**工具使用:**
- 工具: amap_maps_weather
- 参数: city (城市名称或 adcode)

**返回数据说明:**
- forecasts 包含未来几天的天气预报
- 每天包含: 日期、白天天气、夜间天气、温度、风向风力


**重要提示: Meal.type 字段必须使用以下英文枚举值:**
- "breakfast" (早餐)
- "lunch" (午餐)  
- "dinner" (晚餐)
- "snack" (小吃)


**输出格式要求:**
必须返回符合 WeatherInfo 格式的 JSON 数组:
**输出示例:**
[
  {
    "date": "2025-06-01",
    "day_weather": "晴",
    "night_weather": "多云",
    "day_temp": 28,
    "night_temp": 18,
    "wind_direction": "东南风",
    "wind_power": "3级"
  },
  {
    "date": "2025-06-02",
    "day_weather": "小雨",
    "night_weather": "阴",
    "day_temp": 25,
    "night_temp": 17,
    "wind_direction": "北风",
    "wind_power": "4级"
  }
]

**注意:**
- 温度只填数字,不要带°C单位
- 严格按照上述 JSON 格式输出
- 如果工具返回的温度带单位，请去掉单位再输出
"""


HOTEL_AGENT_PROMPT = """你是酒店推荐专家。你的任务是根据城市和住宿偏好推荐合适的酒店。

**工作流程:**
1. 理解用户的住宿需求（经济型/舒适型/豪华型等）
2. 使用 amap_maps_text_search 搜索酒店
3. 从结果中筛选符合要求的酒店
4. 提供价格区间和评分参考

**工具使用:**
- 工具: amap_maps_text_search
- 参数: keywords, city

**搜索策略:**
- 经济型 → keywords="经济酒店 便宜"
- 舒适型 → keywords="酒店 星级酒店"
- 豪华型 → keywords="五星级酒店 高档酒店"
- 默认 → keywords="酒店"

**输出要求:**
- 推荐3-5家酒店
- 包含: 名称、地址、价格区间、评分、类型
- 标注地理位置便利性（如果信息中有）
- 不要编造数据,工具返回什么就返回什么
- 必须返回符合 Hotel 格式的 JSON 数组:
[
{
        "name": "酒店名称1", 
        "address": "酒店地址1", 
        "location": {"longitude": 116.4, "latitude": 39.9},
        "price_range": "200-300元/晚",
        "rating": "4.5",
        "type": "酒店类型",
        "distance": "距离景点2公里",
        "estimated_cost": 250
},
{
        "name": "酒店名称2", 
        "address": "酒店地址2", 
        "location": {"longitude": 116.4, "latitude": 39.0},
        "price_range": "200-300元/晚",
        "rating": "4.5",
        "type": "酒店类型",
        "distance": "距离景点2公里",
        "estimated_cost": 200
}
]
"""


PLANNER_AGENT_PROMPT = """你是旅行行程规划专家。你的任务是根据景点信息和天气信息，生成详细合理的旅行计划。

**数据来源:**
- 景点: 从景点搜索结果中选择
- 美食: 从美食搜索结果中选择餐厅
- 酒店: 从酒店或宾馆的搜索结果中选择
- 天气: 从天气查询结果中获取

**规划原则:**
1. 合理性: 景点之间距离适中，不要来回奔波
2. 多样性: 每天安排不同类型景点（历史文化+自然景观+现代建筑等）
3. 时间安排: 每个景点预留合理游览时间
4. 就近用餐: 午餐安排在景点附近餐厅
5. 预算合理: 根据住宿类型估算酒店费用

**JSON 格式要求:**
- 必须包含所有必需字段
- location 字段使用经纬度格式 {"longitude": 116.4, "latitude": 39.9}
- 门票价格估算: 免费景点0元,一般景区30-100元,知名景点100-200元
- 餐饮费用: 早餐10-20元,午餐20-50元,晚餐50-80元
- **routes 必须是 DayRouteInfo 对象数组，每个 route 包含:**
  - origin: 起点地址 (字符串)
  - destination: 终点地址 (字符串)  
  - distance: 距离公里数 (数字)
  - duration: 预计分钟数 (数字)
  - mode: 交通方式 ("walking", "driving", "transit")

请严格按照以下JSON格式返回旅行计划:
**输出示例结构:**
{
  "city": "城市名称",
  "start_date": "{YYYY-MM-DD}",
  "end_date": "{YYYY-MM-DD}",
  "days": [
    {
      "date": "{YYYY-MM-DD}",
      "day_index": 0,
      "description": "第一天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
      "hotel": {
        "name": "如家酒店", 
        "address": "酒店地址", 
        "location": {"longitude": 116.4, "latitude": 39.9},
        "price_range": "200-300元/晚",
        "rating": "4.5",
        "type": "经济型酒店",
        "distance": "距离景点2公里",
        "estimated_cost": 250
      },
      "attractions": [
        {
          "name": "景点名称", 
          "address": "景点地址",
          "location": {"longitude": 116.397, "latitude": 39.918},
          "visit_duration": 180,
          "description": "景点的详细描述",
          "category": "景点类别",
          "rating": 4.8,
          "ticket_price": 60
        }
      ],
      "meals": [
{
    "type": "breakfast",
    "name": "餐厅名称",
    "address": "详细地址",
    "location": {"longitude": 经度, "latitude": 纬度},
    "description": "特色菜品或餐厅描述（包含2-3个招牌菜）",
    "estimated_cost": 人均消费（元，根据餐厅档次估算：小吃街20-50元，普通餐-厅50-100元，特色餐厅100-200元）
},
{
    "type": "lunch",
    "name": "餐厅名称",
    "address": "详细地址",
    "location": {"longitude": 经度, "latitude": 纬度},
    "description": "特色菜品或餐厅描述（包含2-3个招牌菜）",
    "estimated_cost": 人均消费（元，根据餐厅档次估算：小吃街20-50元，普通餐-厅50-100元，特色餐厅100-200元）
},
{
    "type": "dinner",
    "name": "餐厅名称",
    "address": "详细地址",
    "location": {"longitude": 经度, "latitude": 纬度},
    "description": "特色菜品或餐厅描述（包含2-3个招牌菜）",
    "estimated_cost": 人均消费（元，根据餐厅档次估算：小吃街20-50元，普通餐-厅50-100元，特色餐厅100-200元）
},
{
    "type": "snack",
    "name": "餐厅名称",
    "address": "详细地址",
    "location": {"longitude": 经度, "latitude": 纬度},
    "description": "特色菜品或餐厅描述（包含2-3个招牌菜）",
    "estimated_cost": 人均消费（元，根据餐厅档次估算：小吃街20-50元，普通餐-厅50-100元，特色餐厅100-200元）
}
      ],
      "routes": [
        {
          "origin": "如家酒店",
          "destination": "故宫",
          "distance": 2.5,
          "duration": 15,
          "mode": "walking"
        },
        {
          "origin": "故宫",
          "destination": "天坛",
          "distance": 3.2,
          "duration": 45,
          "mode": "subway"
        }
      ],
      "total_distance": 5.7,
      "total_duration": 60,
      "transport_cost": 8
    }
  ],
  "weather_info": [
    {
      "date": "{YYYY-MM-DD}",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 28,
      "night_temp": 18,
      "wind_direction": "东南风",
      "wind_power": "3级"
    }
  ],
  "overall_suggestions": "总体建议",
  "budget": {
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }
}

**特别注意 - 必填字段:**
- 景点(Attraction)必须包含: name, address, location, visit_duration, description, category
- 景点必须包含 category 字段（如: 历史文化、自然风光、现代建筑、公园等）
- 天气(weather_info)必须包含: date, day_weather, night_weather, day_temp, night_temp, wind_direction, wind_power
- 景点和酒店必须包含准确的经纬度坐标，用于后续路线计算
- 天气信息中的温度必须是纯数字(不要带°C等单位)
- 每天安排2-3个景点
- 考虑景点之间的距离、游览时间和交通方式，避免过度奔波
- 提供实用的交通建议（如：步行、自驾、公交等）
- 提供实用的旅行建议（如：是否需要预约）
- 所有价格估算要合理，不要偏离实际太多
- ***必须包含预算信息***:
   - 景点门票价格(ticket_price)
   - 餐饮预估费用(estimated_cost)
   - 酒店预估费用(estimated_cost)
   - 预算汇总(budget)包含各项总费用
- 不要遗漏任何必填字段！
- 不要编造数据，所有信息必须来自工具返回的结果
"""


ROUTE_AGENT_PROMPT = """你是交通路线规划专家。你的任务是根据酒店位置和每天的景点，计算最优的交通路线。

**工作流程:**
1. 接收起点和终点地址
2. 根据交通方式选择对应的 MCP 工具
3. 解析返回的距离和时间数据
4. 提供简洁的路线摘要

**工具使用:**
- 自驾: amap_maps_direction_driving_by_address
- 步行: amap_maps_direction_walking_by_address
- 公交: amap_maps_direction_transit_integrated_by_address

**参数格式:**
- origin_address: 起点
- origin_city: 起点城市
- destination_address: 终点
- destination_city: 终点城市

**输出要求:**
- 距离（公里）
- 预计时间（分钟）
- 预计费用
- 如有换乘信息，一并提供
"""


class MultiAgentTripPlanner:
    """多智能体旅行规划系统"""

    def __init__(self):
        """初始化多智能体系统"""
        print("🔄 开始初始化多智能体旅行规划系统...")

        try:
            settings = get_settings()
            self.llm = get_llm()

            # 创建本地 MCP 工具 (使用本地 MCP 服务器)
            print("  - 创建本地高德地图 MCP 工具...")
            self.amap_tool = MCPTool(
                name="amap",
                description="高德地图服务",
                server_command=["python", "-m", "app.services.amap_mcp_server"],
                env={"AMAP_API_KEY": settings.amap_api_key},
                auto_expand=True
            )

            # 创建景点搜索Agent
            print("  - 创建景点搜索Agent...")
            self.attraction_agent = SimpleAgent(
                name="景点搜索专家",
                llm=self.llm,
                system_prompt=ATTRACTION_AGENT_PROMPT
            )
            self.attraction_agent.add_tool(self.amap_tool)

            print("  - 创建美食搜索Agent...")
            self.gourmet_agent = SimpleAgent(
                name="美食搜索专家",
                llm=self.llm,
                system_prompt=GOURMET_FOOD_AGENT_PROMPT
            )
            self.gourmet_agent.add_tool(self.amap_tool)

            # 创建天气查询Agent
            print("  - 创建天气查询Agent...")
            self.weather_agent = SimpleAgent(
                name="天气查询专家",
                llm=self.llm,
                system_prompt=WEATHER_AGENT_PROMPT
            )
            self.weather_agent.add_tool(self.amap_tool)

            # 创建酒店推荐Agent
            print("  - 创建酒店推荐Agent...")
            self.hotel_agent = SimpleAgent(
                name="酒店推荐专家",
                llm=self.llm,
                system_prompt=HOTEL_AGENT_PROMPT
            )
            self.hotel_agent.add_tool(self.amap_tool)

            # 创建行程规划Agent(不需要工具)
            print("  - 创建行程规划Agent...")
            self.planner_agent = SimpleAgent(
                name="行程规划专家",
                llm=self.llm,
                system_prompt=PLANNER_AGENT_PROMPT
            )

            # 创建交通路线规划Agent
            print("  - 创建交通路线规划Agent...")
            self.route_agent = SimpleAgent(
                name="交通路线规划专家",
                llm=self.llm,
                system_prompt=ROUTE_AGENT_PROMPT
            )
            self.route_agent.add_tool(self.amap_tool)

            print(f"✅ 多智能体系统初始化成功")
            print(f"   使用本地 MCP 服务器 (app.services.amap_mcp_server)")
            print(f"   旅行规划助手适配了: {len(self.attraction_agent.list_tools())} 个工具")

            # 打印可用的工具名称
            tools = self.attraction_agent.list_tools()
            print(f"   📋 可用工具列表:")
            for tool in tools:
                print(f"      - {tool}")

        except Exception as e:
            print(f"❌ 多智能体系统初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def plan_trip(self, request: TripRequest, progress_callback: Optional[ProgressCallback] = None) -> TripPlan:
        """
        使用多智能体协作生成旅行计划

        Args:
            request: 旅行请求

        Returns:
            旅行计划
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 开始多智能体协作规划旅行...")
            print(f"目的地: {request.city}")
            print(f"日期: {request.start_date} 至 {request.end_date}")
            print(f"天数: {request.travel_days}天")
            print(f"兴趣标签: {', '.join(request.preferences) if request.preferences else '无'}")
            print(f"饮食偏好: {', '.join(request.food_preferences) if request.food_preferences else '无'}")
            print(f"交通方式偏好: {request.transportation if request.transportation else '无'}")
            print(f"住宿偏好: {request.accommodation if request.accommodation else '无'}")
            print(f"就餐环境偏好: {request.environment_preferences if request.environment_preferences else '无'}")

            print(f"{'='*60}\n")

            # 步骤1: 景点搜索Agent搜索景点
            print("📍 步骤1: 搜索景点...")
            attraction_query = self._build_attraction_query(request)
            attraction_response = self.attraction_agent.run(attraction_query)
            print(f"景点搜索结果: {attraction_response}...\n")
            if progress_callback:
                progress_callback.update(1)

            # 步骤2: 美食搜索Agent搜索美食
            print("🍽️ 步骤2: 搜索美食...")
            gourmet_query = self._build_gourmet_query(request)
            try:
                gourmet_response = self.gourmet_agent.run(gourmet_query)
                print(f"美食搜索结果: {gourmet_response}...\n")
            except Exception as e:
                # 如果遇到内容过滤错误，使用默认信息
                if "1301" in str(e) or "contentFilter" in str(e) or "敏感内容" in str(e):
                    print(f"⚠️ 美食搜索被内容过滤拦截，使用默认美食信息")
                    gourmet_response = f"为您推荐{request.city}的特色美食，包括当地小吃、传统菜肴等。"
                else:
                    raise e
            if progress_callback:
                progress_callback.update(2)

            # 步骤3: 天气查询Agent查询天气
            print("🌤️  步骤3: 查询天气...")
            weather_query = f"请查询{request.city}的天气信息"
            weather_response = self.weather_agent.run(weather_query)
            print(f"天气查询结果: {weather_response}...\n")
            if progress_callback:
                progress_callback.update(3)

            # 步骤4: 酒店推荐Agent搜索酒店
            print("🏨 步骤4: 搜索酒店...")
            hotel_query = f"请搜索{request.city}的{request.accommodation}酒店"
            hotel_response = self.hotel_agent.run(hotel_query)
            print(f"酒店搜索结果: {hotel_response}...\n")
            if progress_callback:
                progress_callback.update(4)

            # 步骤5: 行程规划Agent整合信息生成计划
            print("📋 步骤5: 生成行程计划...")
            planner_query = self._build_planner_query(
                request, 
                attraction_response, 
                gourmet_response,
                weather_response, 
                hotel_response
            )
            planner_response = self.planner_agent.run(planner_query)
            print(f"行程规划结果: {planner_response}...\n")
            if progress_callback:
                progress_callback.update(5)

            # 步骤6: 计算每天的交通路线
            print("🚗 步骤6: 计算交通路线...")
            # 先解析基本计划
            trip_plan = self._parse_response(planner_response, request)
            # 计算并添加路线信息
            trip_plan = self._enrich_routes(trip_plan, request)

            # 确保routes不为空
            for day in trip_plan.days:
                print(f"   DEBUG: Day {day.date} has {len(day.routes)} routes")

            if progress_callback:
                progress_callback.update(6)

            print(f"{'='*60}")
            print(f"✅ 旅行计划生成完成!")
            print(f"{'='*60}\n")

            return trip_plan

        except Exception as e:
            error_str = str(e)
            # 检查是否是 MCP JSON-RPC 错误
            if "Failed to parse JSONRPC" in error_str or "JSONRPCMessage" in error_str or "JSONRPC" in error_str:
                print(f"⚠️ MCP服务器响应格式错误: {error_str[:100]}")
                # 尝试返回部分结果
                if 'trip_plan' in locals():
                    return trip_plan
            print(f"❌ 生成旅行计划失败: {error_str[:200]}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_plan(request)

    def _build_attraction_query(self, request: TripRequest) -> str:
        """构建景点搜索查询 - 直接调用 MCP 工具获取数据"""
        search_keywords = ["景点", "风景区", "旅游", "名胜古迹"]
        all_results = []

        for keyword in search_keywords:
            try:
                result = self.amap_tool.run({
                    "action": "call_tool",
                    "tool_name": "amap_maps_text_search",
                    "arguments": {
                        "keywords": keyword,
                        "city": request.city,
                        "citylimit": True
                    }
                })
                all_results.append(f"\n搜索关键词 '{keyword}' 的结果:\n{result}\n")
            except Exception as e:
                all_results.append(f"\n搜索关键词 '{keyword}' 失败: {str(e)}\n")

        results_text = "\n".join(all_results)

        prefs = ", ".join(request.preferences) if request.preferences else "无特殊偏好"

        query = f"""我已经使用高德地图搜索了{request.city}的景点，以下是搜索结果：

{results_text}

请从以上搜索结果中筛选出最热门、评分最高的8-10个景点。

用户偏好: {prefs}

对于每个选中的景点，请提供 JSON 格式的输出，包含：
- name: 景点名称
- address: 详细地址
- location: {{longitude: 经度, latitude: 纬度}}
- rating: 评分（如果没有，估算为 4.0-4.8）
- description: 简要描述（20-50字）
- category: 景点类别（如：历史文化、自然风光、公园、博物馆等）
- visit_duration: 建议游览时间（分钟，如 120-180）
- ticket_price: 门票价格（估算，免费景点为 0）"""
        return query


    def _build_gourmet_query(self, request: TripRequest) -> str:
        """构建美食搜索查询 - 直接调用 MCP 工具获取数据"""
        search_keywords = ["美食", "特色小吃", "本地美食"]
        all_results = []

        for keyword in search_keywords:
            try:
                result = self.amap_tool.run({
                    "action": "call_tool",
                    "tool_name": "amap_maps_text_search",
                    "arguments": {
                        "keywords": keyword,
                        "city": request.city,
                        "citylimit": True
                    }
                })
                all_results.append(f"\n搜索关键词 '{keyword}' 的结果:\n{result}\n")
            except Exception as e:
                all_results.append(f"\n搜索关键词 '{keyword}' 失败: {str(e)}\n")
        
        results_text = "\n".join(all_results)
        
        prefs = ", ".join(request.food_preferences) if request.food_preferences else "无特殊口味偏好"
        
        query = f"""我已经使用高德地图搜索了{request.city}的特色美食，以下是搜索结果：

{results_text}

请从搜索结果中筛选出最受欢迎的10-15个餐厅和美食。

用户偏好: {prefs}

对于每个餐厅，请提供 JSON 格式的输出，包含：
- name: 餐厅名称
- address: 地址
- rating: 评分
- 特色菜品"""
        return query

    
    def _build_planner_query(self, request: TripRequest, attractions: str,
                            gourmet: str, weather: str, hotels: str = "") -> str:
        """构建行程规划查询"""
        query = f"""请根据以下信息生成{request.city}的{request.travel_days}天旅行计划:

**基本信息:**
- 城市: {request.city}
- 日期: {request.start_date} 至 {request.end_date}
- 天数: {request.travel_days}天
- 交通方式: {request.transportation}
- 兴趣标签: {', '.join(request.preferences) if request.preferences else '无'}
- 饮食偏好: {', '.join(request.food_preferences) if request.food_preferences else '无'}
- 交通方式偏好: {request.transportation if request.transportation else '无'}
- 住宿偏好: {request.accommodation if request.accommodation else '无'}
- 就餐环境偏好: {request.environment_preferences if request.environment_preferences else '无'}


**景点信息:**
{attractions}

**美食信息:**
{gourmet}

**天气信息:**
{weather}

**酒店信息:**
{hotels}

**JSON 输出要求:**
1. 必须返回完整的 JSON 对象
2. 景点必须包含: name, address, location, visit_duration, description, category
3. 天气信息必须是 WeatherInfo 格式的对象数组，包含: date, day_weather, night_weather, day_temp, night_temp, wind_direction, wind_power
4. 温度值只填数字，不要带°C单位
5. 餐饮必须包含: type, name, description, estimated_cost
6. 酒店必须包含: name, address, location, price_range, rating, type, estimated_cost

**行程安排:**
1. 每天安排2-3个景点
2. 每天必须包含早中晚三餐，根据美食信息推荐当地特色餐厅
3. 每天推荐一个具体的酒店(从酒店信息中选择)
4. 考虑景点之间的距离和交通方式
5. 景点和酒店的经纬度坐标(location)必须真实准确!
"""
        if request.free_text_input:
            query += f"\n**额外要求:** {request.free_text_input}"

        return query

    def _enrich_routes(self, trip_plan: TripPlan, request: TripRequest) -> TripPlan:
        """为每天的行程添加交通路线信息 - 优先使用 MCP，失败时使用坐标估算"""
        try:
            transportation = request.transportation

            # 映射交通方式到 API 类型
            route_type_map = {
                "自驾": "driving",
                "步行": "walking",
                "公共交通": "transit",
                "打车": "driving",
            }
            route_type = route_type_map.get(transportation, "walking")

            # 定义交通方式的参数: 速度(km/h)、每公里费用（用于回退计算）
            transport_params = {
                "步行": {"speed": 5, "cost_per_km": 0},
                "自驾": {"speed": 30, "cost_per_km": 2},
                "打车": {"speed": 30, "cost_per_km": 3},
                "公共交通": {"speed": 20, "cost_per_km": 0.5},
            }
            params = transport_params.get(transportation, transport_params["步行"])

            for day in trip_plan.days:
                if not day.hotel or not day.attractions:
                    # 如果没有酒店或景点，使用默认值
                    day.routes = []
                    day.total_distance = 0
                    day.total_duration = 0
                    day.transport_cost = 0
                    continue

                routes = []
                total_distance = 0
                total_duration = 0

                # 获取酒店位置
                hotel_loc = day.hotel.location

                # 计算酒店到第一个景点的路线
                try:
                    route = self._calculate_route_via_mcp(
                        origin=day.hotel.address or day.hotel.name,
                        destination=day.attractions[0].address or day.attractions[0].name,
                        city=request.city,
                        route_type=route_type
                    )
                    routes.append(route)
                    total_distance += route.distance
                    total_duration += route.duration
                    print(f"   路线: {day.hotel.name[:10]} -> {day.attractions[0].name[:10]}: {route.distance}km, {route.duration}分钟")
                except Exception as e:
                    print(f"   MCP路线计算失败，使用坐标估算: {e}")
                    # 回退到坐标估算
                    if hotel_loc and day.attractions[0].location:
                        distance = self._calculate_distance_by_coords(
                            hotel_loc.longitude, hotel_loc.latitude,
                            day.attractions[0].location.longitude, day.attractions[0].location.latitude
                        )
                        duration = max(5, int(distance * 60 / params["speed"]))
                    else:
                        distance, duration = 2.0, 15
                    from app.models.schemas import DayRouteInfo
                    routes.append(DayRouteInfo(
                        origin=day.hotel.name,
                        destination=day.attractions[0].name,
                        distance=round(distance, 2),
                        duration=duration,
                        mode=transportation
                    ))
                    total_distance += distance
                    total_duration += duration

                # 计算景点之间的路线
                for i in range(1, len(day.attractions)):
                    try:
                        route = self._calculate_route_via_mcp(
                            origin=day.attractions[i-1].address or day.attractions[i-1].name,
                            destination=day.attractions[i].address or day.attractions[i].name,
                            city=request.city,
                            route_type=route_type
                        )
                        routes.append(route)
                        total_distance += route.distance
                        total_duration += route.duration
                        print(f"   路线: {day.attractions[i-1].name[:10]} -> {day.attractions[i].name[:10]}: {route.distance}km, {route.duration}分钟")
                    except Exception as e:
                        print(f"   MCP路线计算失败，使用坐标估算: {e}")
                        # 回退到坐标估算
                        if day.attractions[i-1].location and day.attractions[i].location:
                            distance = self._calculate_distance_by_coords(
                                day.attractions[i-1].location.longitude, day.attractions[i-1].location.latitude,
                                day.attractions[i].location.longitude, day.attractions[i].location.latitude
                            )
                            duration = max(5, int(distance * 60 / params["speed"]))
                        else:
                            distance, duration = 2.0, 15
                        from app.models.schemas import DayRouteInfo
                        routes.append(DayRouteInfo(
                            origin=day.attractions[i-1].name,
                            destination=day.attractions[i].name,
                            distance=round(distance, 2),
                            duration=duration,
                            mode=transportation
                        ))
                        total_distance += distance
                        total_duration += duration

                # 计算最后一个景点到酒店的路线
                try:
                    route = self._calculate_route_via_mcp(
                        origin=day.attractions[-1].address or day.attractions[-1].name,
                        destination=day.hotel.address or day.hotel.name,
                        city=request.city,
                        route_type=route_type
                    )
                    routes.append(route)
                    total_distance += route.distance
                    total_duration += route.duration
                    print(f"   路线: {day.attractions[-1].name[:10]} -> {day.hotel.name[:10]}: {route.distance}km, {route.duration}分钟")
                except Exception as e:
                    print(f"   MCP路线计算失败，使用坐标估算: {e}")
                    # 回退到坐标估算
                    if day.attractions[-1].location and hotel_loc:
                        distance = self._calculate_distance_by_coords(
                            day.attractions[-1].location.longitude, day.attractions[-1].location.latitude,
                            hotel_loc.longitude, hotel_loc.latitude
                        )
                        duration = max(5, int(distance * 60 / params["speed"]))
                    else:
                        distance, duration = 2.0, 15
                    from app.models.schemas import DayRouteInfo
                    routes.append(DayRouteInfo(
                        origin=day.attractions[-1].name,
                        destination=day.hotel.name,
                        distance=round(distance, 2),
                        duration=duration,
                        mode=transportation
                    ))
                    total_distance += distance
                    total_duration += duration

                # 添加路线信息到 day
                day.routes = routes
                day.total_distance = round(total_distance, 1)
                day.total_duration = int(total_duration)

                # 计算交通费用
                transport_cost = int(total_distance * params["cost_per_km"])
                day.transport_cost = transport_cost

            print(f"✅ 交通路线计算完成")
            return trip_plan

        except Exception as e:
            print(f"⚠️ 路线计算出错: {str(e)}")
            import traceback
            traceback.print_exc()
            # 回退到简单估算值
            return self._enrich_routes_simple_fallback(trip_plan, request)

    def _calculate_route_via_mcp(self, origin: str, destination: str, city: str, route_type: str):
        """使用 MCP 工具计算路线"""
        from app.models.schemas import DayRouteInfo

        # 选择工具名称
        tool_map = {
            "walking": "amap_maps_direction_walking_by_address",
            "driving": "amap_maps_direction_driving_by_address",
            "transit": "amap_maps_direction_transit_integrated_by_address"
        }

        tool_name = tool_map.get(route_type, "amap_maps_direction_walking_by_address")

        # 调用 MCP 工具
        result = self.amap_tool.run({
            "action": "call_tool",
            "tool_name": tool_name,
            "arguments": {
                "origin_address": origin,
                "origin_city": city,
                "destination_address": destination,
                "destination_city": city
            }
        })

        # 解析结果
        distance, duration = self._parse_route_response(result)

        return DayRouteInfo(
            origin=origin,
            destination=destination,
            distance=distance if distance > 0 else 2.0,
            duration=duration if duration > 0 else 15,
            mode=route_type
        )

    def _parse_route_response(self, response: str) -> tuple:
        """从路线响应中提取距离和时间"""
        distance = 0
        duration = 0

        # 尝试直接从 JSON 中提取
        try:
            if '{' in response and '}' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                data = json.loads(json_str)

                # 检查顶层 status
                if data.get("status") == "1":
                    route = data.get("route", {})
                    paths = route.get("paths", [])
                    if paths:
                        path = paths[0]
                        # 距离单位是米，需要转换为公里
                        dist_m = path.get("distance", 0)
                        if isinstance(dist_m, (int, float)) and dist_m > 0:
                            distance = dist_m / 1000
                        # 时间单位是秒，需要转换为分钟
                        dur_s = path.get("duration", 0)
                        if isinstance(dur_s, (int, float)) and dur_s > 0:
                            duration = dur_s / 60

                    # 公交路线的格式不同
                    transits = route.get("transits", [])
                    if transits:
                        transit = transits[0]
                        dist_m = transit.get("distance", 0)
                        if isinstance(dist_m, (int, float)) and dist_m > 0:
                            distance = dist_m / 1000
                        dur_s = transit.get("duration", 0)
                        if isinstance(dur_s, (int, float)) and dur_s > 0:
                            duration = dur_s / 60
        except Exception as e:
            print(f"   JSON解析失败: {e}")

        # 如果 JSON 解析失败，尝试正则匹配
        if distance == 0 or duration == 0:
            # 尝试匹配距离 (公里)
            distance_match = re.search(r'(\d+\.?\d*)\s*公里', response)
            if distance_match:
                distance = float(distance_match.group(1))

            # 尝试匹配时间 (分钟)
            duration_match = re.search(r'(\d+)\s*分钟', response)
            if duration_match:
                duration = int(duration_match.group(1))

        return distance, duration

    def _calculate_distance_by_coords(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """计算两点之间的直线距离（公里）- 使用 Haversine 公式"""
        # 将经纬度转换为弧度
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        # Haversine 公式
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # 地球半径（公里）
        r = 6371

        # 直线距离，城市道路实际距离约为直线距离的 1.4 倍
        return c * r * 1.4

    def _enrich_routes_simple_fallback(self, trip_plan: TripPlan, request: TripRequest) -> TripPlan:
        """使用简单估算值的路线计算回退方案"""
        transportation = request.transportation

        # 定义每段路的默认值
        default_distance = 2.0  # 公里
        default_duration = 15   # 分钟

        # 费用计算
        if transportation == "自驾":
            cost_per_segment = int(default_distance * 2)
        elif transportation == "打车":
            cost_per_segment = int(default_distance * 3)
        elif transportation == "步行":
            cost_per_segment = 0
        else:  # 公共交通
            cost_per_segment = int(default_duration * 0.5)

        for day in trip_plan.days:
            routes = []
            num_segments = len(day.attractions) + 1 if day.attractions else 0  # 酒店->景点...->酒店

            for _ in range(num_segments):
                from app.models.schemas import DayRouteInfo
                routes.append(DayRouteInfo(
                    origin="起点",
                    destination="终点",
                    distance=default_distance,
                    duration=default_duration,
                    mode=transportation
                ))

            day.routes = routes
            day.total_distance = round(num_segments * default_distance, 1)
            day.total_duration = num_segments * default_duration
            day.transport_cost = num_segments * cost_per_segment

        print(f"⚠️ 交通路线计算完成 (使用简单估算值)")
        return trip_plan

    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """
        解析Agent响应

        Args:
            response: Agent响应文本
            request: 原始请求

        Returns:
            旅行计划
        """
        try:
            # 尝试从响应中提取JSON
            # 查找JSON代码块
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                # 直接查找JSON对象
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("响应中未找到JSON数据")

            # 解析JSON
            data = json.loads(json_str)

            # 转换为TripPlan对象
            trip_plan = TripPlan(**data)

            return trip_plan

        except Exception as e:
            print(f"⚠️  解析响应失败: {str(e)}")
            print(f"   将使用备用方案生成计划")
            return self._create_fallback_plan(request)

    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """创建备用计划(当Agent失败时)"""
        from datetime import datetime, timedelta

        # 解析日期
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        # 创建每日行程
        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)

            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"第{i+1}天行程",
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=[
                    Attraction(
                        name=f"{request.city}景点{j+1}",
                        address=f"{request.city}市",
                        location=Location(longitude=116.4 + i*0.01 + j*0.005, latitude=39.9 + i*0.01 + j*0.005),
                        visit_duration=120,
                        description=f"这是{request.city}的著名景点",
                        category="景点"
                    )
                    for j in range(2)
                ],
                meals=[
                    Meal(type="breakfast", name=f"第{i+1}天早餐", description="当地特色早餐"),
                    Meal(type="lunch", name=f"第{i+1}天午餐", description="午餐推荐"),
                    Meal(type="dinner", name=f"第{i+1}天晚餐", description="晚餐推荐")
                ]
            )
            days.append(day_plan)

        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions=f"这是为您规划的{request.city}{request.travel_days}日游行程,建议提前查看各景点的开放时间。"
        )


# 全局多智能体系统实例
_multi_agent_planner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """获取多智能体旅行规划系统实例(单例模式)"""
    global _multi_agent_planner

    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()

    return _multi_agent_planner
