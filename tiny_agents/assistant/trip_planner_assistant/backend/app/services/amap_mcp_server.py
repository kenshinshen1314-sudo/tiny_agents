"""本地高德地图 MCP 服务器

这个 MCP 服务器直接调用高德地图 REST API 并返回正确格式的 JSON，
解决 amap-mcp-server 的 JSON 格式问题（单引号 vs 双引号）。
"""

import asyncio
import json
from typing import Any, Sequence
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

import os
import aiohttp
from datetime import datetime, timedelta

import dotenv

# 加载环境变量
dotenv.load_dotenv()

# 高德地图 REST API 基础 URL
AMAP_BASE_URL = "https://restapi.amap.com"

# 从环境变量获取 API Key
AMAP_API_KEY = os.environ.get("AMAP_API_KEY", "")
if not AMAP_API_KEY:
    raise ValueError("AMAP_API_KEY 环境变量未设置")


class AmapMCPWrapper:
    """高德地图 API 包装器"""

    def __init__(self):
        self.api_key = AMAP_API_KEY

    async def _request(self, endpoint: str, params: dict) -> dict:
        """发送 HTTP 请求到高德地图 API"""
        url = f"{AMAP_BASE_URL}{endpoint}"
        params["key"] = self.api_key

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

                # 检查响应状态
                if data.get("status") != "1":
                    error_msg = data.get("info", "未知错误")
                    return {"error": error_msg, "status": "0"}

                return data

    async def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> str:
        """搜索 POI"""
        params = {
            "keywords": keywords,
            "city": city,
            "citylimit": "true" if citylimit else "false",
            "output": "json",
            "offset": 20,
            "page": 1,
        }

        data = await self._request("/v3/place/text", params)
        # 返回 JSON 字符串，确保使用双引号
        return json.dumps(data, ensure_ascii=False)

    async def get_weather(self, city: str) -> str:
        """查询天气"""
        params = {"city": city, "extensions": "all", "output": "json"}
        data = await self._request("/v3/weather/weatherInfo", params)
        return json.dumps(data, ensure_ascii=False)

    async def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: str = None,
        destination_city: str = None,
        route_type: str = "walking"
    ) -> str:
        """规划路线

        route_type: walking, driving, transit
        """
        # 先进行地理编码
        origin_loc = await self.geocode(origin_address, origin_city)
        dest_loc = await self.geocode(destination_address, destination_city)

        if not origin_loc or not dest_loc:
            return json.dumps({"error": "无法解析地址", "status": "0"}, ensure_ascii=False)

        # 根据路线类型选择 API
        if route_type == "driving":
            endpoint = "/v3/direction/driving"
        elif route_type == "transit":
            endpoint = "/v3/direction/transit/integrated"
        else:
            endpoint = "/v3/direction/walking"

        # 构建坐标字符串
        origin_str = f"{origin_loc['longitude']},{origin_loc['latitude']}"
        dest_str = f"{dest_loc['longitude']},{dest_loc['latitude']}"

        params = {
            "origin": origin_str,
            "destination": dest_str,
            "output": "json",
        }

        # 公交路线需要城市参数
        if route_type == "transit" and origin_city:
            params["city"] = origin_city
        elif route_type == "transit":
            params["cityd"] = origin_address

        data = await self._request(endpoint, params)
        return json.dumps(data, ensure_ascii=False)

    async def geocode(self, address: str, city: str = None) -> dict:
        """地理编码"""
        params = {"address": address, "output": "json"}
        if city:
            params["city"] = city

        data = await self._request("/v3/geocode/geo", params)

        geocodes = data.get("geocodes", [])
        if not geocodes:
            return None

        location = geocodes[0].get("location", "")
        if "," in location:
            lon_str, lat_str = location.split(",")
            return {"longitude": float(lon_str), "latitude": float(lat_str)}

        return None


# 创建 MCP 服务器
server = Server("amap-local")
wrapper = AmapMCPWrapper()


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """列出可用资源"""
    return []


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """读取资源"""
    return "未实现资源读取"


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="maps_text_search",
            description="搜索POI（兴趣点），支持按关键词搜索景点、酒店、餐厅等",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "搜索关键词，如：故宫、酒店、餐厅等"
                    },
                    "city": {
                        "type": "string",
                        "description": "城市名称，如：北京、上海"
                    },
                    "citylimit": {
                        "type": "boolean",
                        "description": "是否限制在城市范围内",
                        "default": True
                    }
                },
                "required": ["keywords", "city"]
            }
        ),
        Tool(
            name="maps_weather",
            description="查询指定城市的天气信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如：北京、上海"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="maps_direction_walking_by_address",
            description="规划步行路线（通过地址）",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin_address": {"type": "string", "description": "起点地址"},
                    "origin_city": {"type": "string", "description": "起点城市"},
                    "destination_address": {"type": "string", "description": "终点地址"},
                    "destination_city": {"type": "string", "description": "终点城市"}
                },
                "required": ["origin_address", "destination_address"]
            }
        ),
        Tool(
            name="maps_direction_driving_by_address",
            description="规划驾车路线（通过地址）",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin_address": {"type": "string", "description": "起点地址"},
                    "origin_city": {"type": "string", "description": "起点城市"},
                    "destination_address": {"type": "string", "description": "终点地址"},
                    "destination_city": {"type": "string", "description": "终点城市"}
                },
                "required": ["origin_address", "destination_address"]
            }
        ),
        Tool(
            name="maps_direction_transit_integrated_by_address",
            description="规划公交路线（通过地址）",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin_address": {"type": "string", "description": "起点地址"},
                    "origin_city": {"type": "string", "description": "起点城市"},
                    "destination_address": {"type": "string", "description": "终点地址"},
                    "destination_city": {"type": "string", "description": "终点城市"}
                },
                "required": ["origin_address", "destination_address"]
            }
        ),
        Tool(
            name="maps_geo",
            description="地理编码：将地址转换为经纬度坐标",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {"type": "string", "description": "地址"},
                    "city": {"type": "string", "description": "城市（可选）"}
                },
                "required": ["address"]
            }
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """处理工具调用"""

    # 参数类型转换函数
    def to_bool(value):
        """将各种boolean表示转换为Python boolean"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        if isinstance(value, (int, float)):
            return bool(value)
        return False

    try:
        # 参数验证和日志
        import logging
        logger = logging.getLogger(__name__)

        if name == "maps_text_search":
            # 验证必需参数
            keywords = arguments.get("keywords")
            city = arguments.get("city")

            if not keywords or not city:
                error_msg = f"参数缺失: keywords={keywords}, city={city}"
                logger.error(f"maps_text_search {error_msg}")
                return [TextContent(type="text", text=json.dumps({
                    "error": error_msg,
                    "status": "0",
                    "info": "缺少必需参数"
                }, ensure_ascii=False))]

            # 转换citylimit参数为Python boolean
            citylimit = arguments.get("citylimit", True)
            citylimit = to_bool(citylimit)

            logger.info(f"maps_text_search: keywords={keywords}, city={city}, citylimit={citylimit}")

            result = await wrapper.search_poi(
                keywords=keywords,
                city=city,
                citylimit=citylimit
            )
            return [TextContent(type="text", text=result)]

        elif name == "maps_weather":
            # 验证必需参数
            city = arguments.get("city")
            if not city:
                error_msg = "参数缺失: city"
                logger.error(f"maps_weather {error_msg}")
                return [TextContent(type="text", text=json.dumps({
                    "error": error_msg,
                    "status": "0",
                    "info": "缺少必需参数city"
                }, ensure_ascii=False))]

            logger.info(f"maps_weather: city={city}")
            result = await wrapper.get_weather(city=city)
            return [TextContent(type="text", text=result)]

        elif name == "maps_direction_walking_by_address":
            # 验证必需参数
            origin_address = arguments.get("origin_address")
            destination_address = arguments.get("destination_address")
            if not origin_address or not destination_address:
                error_msg = f"参数缺失: origin_address={origin_address}, destination_address={destination_address}"
                logger.error(f"maps_direction_walking_by_address {error_msg}")
                return [TextContent(type="text", text=json.dumps({
                    "error": error_msg,
                    "status": "0",
                    "info": "缺少必需参数"
                }, ensure_ascii=False))]

            logger.info(f"maps_direction_walking_by_address: {origin_address} -> {destination_address}")
            result = await wrapper.plan_route(
                origin_address=origin_address,
                destination_address=destination_address,
                origin_city=arguments.get("origin_city"),
                destination_city=arguments.get("destination_city"),
                route_type="walking"
            )
            return [TextContent(type="text", text=result)]

        elif name == "maps_direction_driving_by_address":
            # 验证必需参数
            origin_address = arguments.get("origin_address")
            destination_address = arguments.get("destination_address")
            if not origin_address or not destination_address:
                error_msg = f"参数缺失: origin_address={origin_address}, destination_address={destination_address}"
                logger.error(f"maps_direction_driving_by_address {error_msg}")
                return [TextContent(type="text", text=json.dumps({
                    "error": error_msg,
                    "status": "0",
                    "info": "缺少必需参数"
                }, ensure_ascii=False))]

            logger.info(f"maps_direction_driving_by_address: {origin_address} -> {destination_address}")
            result = await wrapper.plan_route(
                origin_address=origin_address,
                destination_address=destination_address,
                origin_city=arguments.get("origin_city"),
                destination_city=arguments.get("destination_city"),
                route_type="driving"
            )
            return [TextContent(type="text", text=result)]

        elif name == "maps_direction_transit_integrated_by_address":
            # 验证必需参数
            origin_address = arguments.get("origin_address")
            destination_address = arguments.get("destination_address")
            if not origin_address or not destination_address:
                error_msg = f"参数缺失: origin_address={origin_address}, destination_address={destination_address}"
                logger.error(f"maps_direction_transit_integrated_by_address {error_msg}")
                return [TextContent(type="text", text=json.dumps({
                    "error": error_msg,
                    "status": "0",
                    "info": "缺少必需参数"
                }, ensure_ascii=False))]

            logger.info(f"maps_direction_transit_integrated_by_address: {origin_address} -> {destination_address}")
            result = await wrapper.plan_route(
                origin_address=origin_address,
                destination_address=destination_address,
                origin_city=arguments.get("origin_city"),
                destination_city=arguments.get("destination_city"),
                route_type="transit"
            )
            return [TextContent(type="text", text=result)]

        elif name == "maps_geo":
            # 验证必需参数
            address = arguments.get("address")
            if not address:
                error_msg = "参数缺失: address"
                logger.error(f"maps_geo {error_msg}")
                return [TextContent(type="text", text=json.dumps({
                    "error": error_msg,
                    "status": "0",
                    "info": "缺少必需参数address"
                }, ensure_ascii=False))]

            logger.info(f"maps_geo: address={address}")
            result = await wrapper.geocode(
                address=address,
                city=arguments.get("city")
            )
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

        else:
            error_msg = f"未知工具: {name}"
            logger.error(error_msg)
            return [TextContent(type="text", text=json.dumps({
                "error": error_msg,
                "status": "0",
                "info": f"工具'{name}'不存在"
            }, ensure_ascii=False))]

    except Exception as e:
        logger.exception(f"工具调用异常: {name}")
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "status": "0",
            "info": "工具调用失败"
        }, ensure_ascii=False))]


async def main():
    """启动 MCP 服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="amap-local",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
