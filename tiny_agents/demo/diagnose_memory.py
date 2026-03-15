"""
记忆系统诊断脚本

用于诊断记忆检索问题，检查：
1. Qdrant 连接状态
2. Collection 信息（向量数量、维度）
3. 列出所有存储的记忆（不带 user_id 过滤）
4. 测试向量检索
"""

import logging
import json
from typing import Dict, Any, List

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def diagnose_qdrant() -> Dict[str, Any]:
    """诊断 Qdrant 向量存储"""
    from tiny_agents.memory.storage.qdrant_store import QdrantConnectionManager

    results = {
        "qdrant_connection": False,
        "collection_info": {},
        "all_points": [],
        "test_search": {}
    }

    try:
        logger.info("=" * 60)
        logger.info("🔍 记忆系统诊断")
        logger.info("=" * 60)

        # 1. 检查连接
        logger.info("\n1️⃣ 检查 Qdrant 连接...")
        try:
            vector_store = QdrantConnectionManager.get_instance(
                collection_name="tiny_agents_vectors"
            )
            results["qdrant_connection"] = True
            logger.info("   ✅ Qdrant 连接成功")
        except Exception as e:
            logger.error(f"   ❌ Qdrant 连接失败: {e}")
            return results

        # 2. 获取集合信息
        logger.info("\n2️⃣ 获取集合信息...")
        try:
            collection_info = vector_store.get_collection_info()
            results["collection_info"] = collection_info
            logger.info(f"   ✅ Collection 名称: {collection_info.get('name')}")
            logger.info(f"   📊 向量总数: {collection_info.get('points_count', 0)}")
            logger.info(f"   📐 向量维度: {collection_info.get('config', {}).get('vector_size', 'unknown')}")
            logger.info(f"   📏 距离度量: {collection_info.get('config', {}).get('distance', 'unknown')}")

            if collection_info.get('points_count', 0) == 0:
                logger.warning("   ⚠️ Collection 为空！没有任何向量数据")
                logger.info("   💡 提示: 请先添加一些记忆数据")
        except Exception as e:
            logger.error(f"   ❌ 获取集合信息失败: {e}")

        # 3. 列出所有记忆点（不带过滤）
        logger.info("\n3️⃣ 列出所有存储的记忆点...")
        try:
            # 使用 scroll API 获取所有点
            all_points = []
            offset = None
            limit = 100

            while True:
                if hasattr(vector_store.client, 'scroll'):
                    # 新版 API
                    scroll_result = vector_store.client.scroll(
                        collection_name=vector_store.collection_name,
                        limit=limit,
                        offset=offset,
                        with_payload=True,
                        with_vectors=False
                    )
                    points = scroll_result[0]  # points
                    offset = scroll_result[1]  # next_page_offset
                else:
                    break

                all_points.extend(points)
                if offset is None:
                    break

            results["all_points"] = all_points
            logger.info(f"   📦 总共找到 {len(all_points)} 个记忆点")

            # 按 memory_type 分组统计
            memory_type_counts = {}
            user_id_counts = {}

            for point in all_points:
                payload = point.payload or {}
                memory_type = payload.get("memory_type", "unknown")
                user_id = payload.get("user_id", "unknown")
                memory_type_counts[memory_type] = memory_type_counts.get(memory_type, 0) + 1
                user_id_counts[user_id] = user_id_counts.get(user_id, 0) + 1

            logger.info(f"   📋 按 memory_type 分组:")
            for mtype, count in memory_type_counts.items():
                logger.info(f"      - {mtype}: {count} 条")

            logger.info(f"   👤 按 user_id 分组:")
            for uid, count in user_id_counts.items():
                logger.info(f"      - {uid}: {count} 条")

            # 显示前几条记忆的详细信息
            logger.info(f"\n   📝 前 5 条记忆详情:")
            for i, point in enumerate(all_points[:5]):
                payload = point.payload or {}
                content = payload.get("content", "")[:50]
                memory_id = payload.get("memory_id", "N/A")[:8]
                user_id = payload.get("user_id", "N/A")
                memory_type = payload.get("memory_type", "N/A")
                logger.info(f"      [{i+1}] memory_id={memory_id}... | user_id={user_id} | type={memory_type}")
                logger.info(f"          content: {content}...")

        except Exception as e:
            logger.error(f"   ❌ 列出记忆点失败: {e}")

        # 4. 测试向量检索 - 不带 user_id 过滤
        logger.info("\n4️⃣ 测试向量检索（不带 user_id 过滤）...")
        try:
            from tiny_agents.memory.embedding import get_text_embedder

            embedder = get_text_embedder()
            test_query = "人工智能"
            query_vector = embedder.encode(test_query).tolist()

            # 测试1: 不带任何过滤
            logger.info(f"   测试查询: '{test_query}'")
            logger.info(f"   查询向量维度: {len(query_vector)}")

            results_no_filter = vector_store.search_similar(
                query_vector=query_vector,
                limit=5,
                where=None
            )

            logger.info(f"   🔍 不带过滤 - 返回 {len(results_no_filter)} 个结果:")
            for i, r in enumerate(results_no_filter[:3]):
                payload = r.get('metadata', {})
                logger.info(f"      [{i+1}] score={r.get('score', 0):.4f}, user_id={payload.get('user_id')}, type={payload.get('memory_type')}")
                logger.info(f"          content: {payload.get('content', '')[:40]}...")

            results["test_search"]["no_filter"] = results_no_filter

            # 测试2: 只带 memory_type 过滤
            logger.info(f"\n   🔍 只带 memory_type='semantic' 过滤:")
            results_semantic = vector_store.search_similar(
                query_vector=query_vector,
                limit=5,
                where={"memory_type": "semantic"}
            )
            logger.info(f"      返回 {len(results_semantic)} 个结果")

            results["test_search"]["semantic_only"] = results_semantic

            # 测试3: 带 user_id 过滤
            logger.info(f"\n   🔍 带 user_id='user123' 过滤:")
            results_with_user = vector_store.search_similar(
                query_vector=query_vector,
                limit=5,
                where={"memory_type": "semantic", "user_id": "user123"}
            )
            logger.info(f"      返回 {len(results_with_user)} 个结果")
            if results_with_user:
                for i, r in enumerate(results_with_user[:3]):
                    payload = r.get('metadata', {})
                    logger.info(f"         [{i+1}] score={r.get('score', 0):.4f}")
                    logger.info(f"            content: {payload.get('content', '')[:40]}...")

            results["test_search"]["with_user"] = results_with_user

        except Exception as e:
            logger.error(f"   ❌ 向量检索测试失败: {e}")

        # 5. 诊断建议
        logger.info("\n5️⃣ 诊断建议...")
        points_count = results["collection_info"].get("points_count", 0)

        if points_count == 0:
            logger.warning("   ⚠️ Collection 为空 - 没有数据可供检索")
            logger.info("   💡 建议: 先运行 memory_demo.py 添加一些测试数据")
        elif results["test_search"].get("no_filter") and len(results["test_search"]["no_filter"]) > 0:
            if results["test_search"].get("with_user") and len(results["test_search"]["with_user"]) == 0:
                logger.warning("   ⚠️ user_id 过滤导致没有结果")
                logger.info("   💡 可能原因:")
                logger.info("      - 添加记忆时的 user_id 与查询时的 user_id 不一致")
                logger.info("      - 检查上面 '按 user_id 分组' 的输出")
                logger.info("   💡 解决方案:")
                logger.info("      - 确保 MemoryTool 初始化时的 user_id 与添加/查询时一致")
                logger.info("      - 或者在查询时不指定 user_id 参数")
        else:
            logger.warning("   ⚠️ 向量检索返回空结果")
            logger.info("   💡 可能原因:")
            logger.info("      - 查询向量与存储向量相似度太低")
            logger.info("      - 向量维度不匹配")

    except Exception as e:
        logger.error(f"❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()

    return results


def main():
    """主函数"""
    results = diagnose_qdrant()

    # 保存诊断结果到文件
    output_file = "/tmp/memory_diagnosis.json"
    try:
        # 转换不可序列化的对象
        serializable_results = {
            "qdrant_connection": results["qdrant_connection"],
            "collection_info": results["collection_info"],
            "points_count": len(results.get("all_points", [])),
            "test_search_results": {
                "no_filter_count": len(results.get("test_search", {}).get("no_filter", [])),
                "semantic_only_count": len(results.get("test_search", {}).get("semantic_only", [])),
                "with_user_count": len(results.get("test_search", {}).get("with_user", [])),
            }
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        logger.info(f"\n📄 诊断结果已保存到: {output_file}")
    except Exception as e:
        logger.warning(f"保存诊断结果失败: {e}")

    logger.info("\n" + "=" * 60)
    logger.info("✅ 诊断完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
