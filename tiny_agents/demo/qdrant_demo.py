"""
Qdrant 向量数据库演示
展示如何使用 Qdrant 进行文档的向量化存储和检索

注意：如果遇到 SSL 错误，可以尝试：
1. 使用本地 Qdrant: docker run -p 6333:6333 qdrant/qdrant
2. 或设置 QDRANT_URL=http://localhost:6333

Qdrant 云服务端口说明：
- 端口 443: REST API (HTTPS)
- 端口 6333: gRPC API (可能存在 SSL 兼容性问题)
"""
import os
import logging
import numpy as np
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Distance, VectorParams

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 从环境变量获取配置
url = os.getenv("QDRANT_URL")
api_key = os.getenv("QDRANT_API_KEY")
collection_name = os.getenv("QDRANT_COLLECTION", "demo_collection")
timeout = int(os.getenv("QDRANT_TIMEOUT", "30"))

# 验证配置
if not url:
    raise ValueError("QDRANT_URL 环境变量必须设置")
if not api_key:
    raise ValueError("QDRANT_API_KEY 环境变量必须设置")
if not collection_name:
    raise ValueError("集合名称不能为空")

logger.info(f"连接到 Qdrant: {url}")
logger.info(f"使用集合: {collection_name}")

# 向量维度（从环境变量读取）
vector_size = int(os.getenv("QDRANT_VECTOR_SIZE", "384"))

try:
    # 创建 Qdrant 客户端
    client = QdrantClient(
        url=url,
        api_key=api_key,
        timeout=timeout,
        prefer_grpc=False,  # 使用 HTTP REST API
    )
    logger.info("✅ 成功创建 Qdrant 客户端")

    # 测试连接
    logger.info("测试连接...")
    collections = client.get_collections().collections
    logger.info(f"✅ 连接成功！现有 {len(collections)} 个集合")

    # 检查集合是否存在，不存在则创建
    collection_names = [c.name for c in collections]

    if collection_name not in collection_names:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        logger.info(f"✅ 创建集合: {collection_name}")
    else:
        logger.info(f"✅ 使用现有集合: {collection_name}")

    # 准备测试数据 - 使用随机向量作为示例
    # 在实际应用中，你需要使用 embedding 模型将文本转换为向量
    np.random.seed(42)
    points = [
        PointStruct(
            id=1,
            payload={
                "topic": "cooking",
                "type": "dessert",
                "text": "Recipe for baking chocolate chip cookies requires flour, sugar, eggs, and chocolate chips."
            },
            vector=np.random.rand(vector_size).tolist()
        ),
        PointStruct(
            id=2,
            payload={
                "topic": "cooking",
                "type": "main_course",
                "text": "How to make a delicious pasta with tomato sauce and basil."
            },
            vector=np.random.rand(vector_size).tolist()
        ),
        PointStruct(
            id=3,
            payload={
                "topic": "sports",
                "type": "basketball",
                "text": "Basketball is a team sport played with a ball and a hoop."
            },
            vector=np.random.rand(vector_size).tolist()
        ),
    ]

    # 插入数据
    logger.info(f"插入 {len(points)} 个数据点...")
    client.upsert(collection_name=collection_name, points=points)
    logger.info("✅ 数据插入成功")

    # 查询数据 - 使用一个查询向量
    query_vector = np.random.rand(vector_size).tolist()
    logger.info("查询数据...")

    # 使用 query_points 方法（推荐）
    search_results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=3,
        with_payload=True
    )

    # 打印结果 - QueryResponse.points 包含结果列表
    points_list = search_results.points
    logger.info(f"查询结果: 找到 {len(points_list)} 个匹配")
    for i, point in enumerate(points_list):
        logger.info(f"  结果 {i + 1}:")
        logger.info(f"    score: {point.score:.4f}")
        logger.info(f"    payload: {point.payload}")

    # 获取集合信息
    collection_info = client.get_collection(collection_name)
    logger.info(f"\n集合信息:")
    logger.info(f"  名称: {collection_info.config.params.vectors.size}")
    logger.info(f"  向量维度: {collection_info.config.params.vectors.size}")
    logger.info(f"  点数量: {collection_info.points_count}")
    logger.info(f"  距离度量: {collection_info.config.params.vectors.distance.value}")

except Exception as e:
    logger.error(f"❌ 错误: {e}")
    logger.error(f"错误类型: {type(e).__name__}")
    raise
