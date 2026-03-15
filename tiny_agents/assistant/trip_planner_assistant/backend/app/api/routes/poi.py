"""POI相关API路由"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from ...services.amap_service import get_amap_service
from ...services.unsplash_service import get_unsplash_service

router = APIRouter(prefix="/poi", tags=["POI"])


class POIDetailResponse(BaseModel):
    """POI详情响应"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.get(
    "/detail/{poi_id}",
    response_model=POIDetailResponse,
    summary="获取POI详情",
    description="根据POI ID获取详细信息,包括图片"
)
async def get_poi_detail(poi_id: str):
    """
    获取POI详情

    Args:
        poi_id: POI ID

    Returns:
        POI详情响应
    """
    try:
        amap_service = get_amap_service()

        # 调用高德地图POI详情API
        result = amap_service.get_poi_detail(poi_id)

        return POIDetailResponse(
            success=True,
            message="获取POI详情成功",
            data=result
        )

    except Exception as e:
        print(f"❌ 获取POI详情失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取POI详情失败: {str(e)}"
        )


@router.get(
    "/search",
    summary="搜索POI",
    description="根据关键词搜索POI"
)
async def search_poi(
    keywords: str = Query(..., description="搜索关键词"),
    city: str = Query("北京", description="城市名称")
):
    """
    搜索POI

    Args:
        keywords: 搜索关键词
        city: 城市名称

    Returns:
        搜索结果
    """
    try:
        amap_service = get_amap_service()
        result = amap_service.search_poi(keywords, city)

        return {
            "success": True,
            "message": "搜索成功",
            "data": result
        }

    except Exception as e:
        print(f"❌ 搜索POI失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"搜索POI失败: {str(e)}"
        )


@router.get(
    "/photo",
    summary="获取景点图片",
    description="根据景点名称、类别和城市从Unsplash获取图片，支持中文景点名称智能匹配"
)
async def get_attraction_photo(
    name: str = Query(..., description="景点名称（支持中文）"),
    category: Optional[str] = Query(None, description="景点类别（如：寺庙、公园、博物馆等）"),
    city: Optional[str] = Query(None, description="城市名称（用于提供搜索上下文）")
):
    """
    获取景点图片

    Args:
        name: 景点名称（支持中文）
        category: 景点类别（可选，如"寺庙"、"公园"、"博物馆"等）
        city: 城市名称（可选，用于提供搜索上下文）

    Returns:
        图片URL
    """
    try:
        unsplash_service = get_unsplash_service()

        # 调用优化后的 Unsplash 服务
        photo_url = unsplash_service.get_photo_url(name, category, city)

        return {
            "success": True,
            "message": "获取图片成功" if photo_url else "未找到匹配图片",
            "data": {
                "name": name,
                "category": category,
                "city": city,
                "photo_url": photo_url
            }
        }

    except Exception as e:
        print(f"❌ 获取景点图片失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取景点图片失败: {str(e)}"
        )


def _contains_city_name(attraction_name: str, city: str) -> bool:
    """检查景点名称是否已包含城市名"""
    # 移除常见的后缀（如市、区等）进行比较
    city_clean = city.replace('市', '').replace('区', '').replace('县', '')
    return city_clean in attraction_name
