# 记忆系统调试指南

## 概述

本文档说明如何使用新增的调试功能来诊断记忆检索问题。

## 已实施的修复

### 1. 详细的向量搜索日志

在 `memory/types/semantic.py` 的 `_vector_search()` 方法中添加了详细的调试日志：

```python
logger.info(f"🔍 [向量搜索] 开始查询: query='{query}', limit={limit}, user_id='{user_id}'")
logger.info(f"🔍 [向量搜索] 查询向量维度: {query_vector_dim}")
logger.info(f"🔍 [向量搜索] 过滤条件: {where_filter}")
logger.info(f"🔍 [向量搜索] 集合信息: points=..., vector_size=...")
logger.info(f"🔍 [向量搜索] Qdrant原始返回 {len(results)} 个结果")
```

### 2. 改进的错误提示

在 `tools/builtin/memory_tool.py` 中改进了搜索失败时的提示信息：

```
🔍 未找到与 'xxx' 相关的记忆

💡 搜索参数:
   - user_id: xxx
   - memory_types: xxx
   - min_importance: xxx

💡 可能的原因:
   1. 数据库中没有相关数据
   2. user_id 不匹配
   3. memory_type 不匹配

💡 调试建议:
   - 运行: python demo/diagnose_memory.py
   - 或在查询时尝试不指定 user_id 参数
```

### 3. 诊断脚本

创建了 `demo/diagnose_memory.py` 诊断脚本，可以检查：
- Qdrant 连接状态
- Collection 信息（向量数量、维度）
- 列出所有存储的记忆（不带 user_id 过滤）
- 测试向量检索（不同过滤条件）

### 4. Debug 模式

在 `SemanticMemory.retrieve()` 方法中添加了 `debug=True` 参数支持：

```python
results = semantic_memory.retrieve(
    query="人工智能",
    limit=5,
    user_id="user123",
    debug=True  # 启用详细调试输出
)
```

## 使用方法

### 方法 1: 运行诊断脚本

```bash
# 设置环境变量（如果使用云服务）
export QDRANT_URL="your_qdrant_url"
export QDRANT_API_KEY="your_api_key"

# 运行诊断脚本
python demo/diagnose_memory.py
```

### 方法 2: 查看详细日志

在代码中启用 INFO 级别日志：

```python
import logging
logging.basicConfig(level=logging.INFO)

from tiny_agents.tools.builtin.memory_tool import MemoryTool

memory_tool = MemoryTool(user_id="user123")
result = memory_tool.execute(
    action="search",
    query="人工智能",
    limit=5
)
```

### 方法 3: 使用 debug 参数

```python
from tiny_agents.memory import MemoryManager
from tiny_agents.memory.types.semantic import SemanticMemory

semantic_memory = SemanticMemory()
results = semantic_memory.retrieve(
    query="人工智能",
    limit=5,
    debug=True  # 输出详细的调试信息
)
```

## 常见问题诊断

### 问题 1: 返回 0 条结果

**症状**: `INFO: ✅ 检索到 0 条相关记忆`

**排查步骤**:

1. 检查集合中是否有数据：
   ```
   INFO: 🔍 [向量搜索] 集合信息: points=0, ...
   ```
   - 如果 points=0，说明没有添加任何记忆

2. 检查 user_id 是否匹配：
   ```
   INFO: 🔍 [向量搜索] 过滤条件: {'memory_type': 'semantic', 'user_id': 'user123'}
   ```
   - 确保添加记忆和查询时使用相同的 user_id

3. 检查原始返回：
   ```
   INFO: 🔍 [向量搜索] Qdrant原始返回 0 个结果
   ```
   - 如果 Qdrant 返回 0 个结果，说明过滤条件太严格

### 问题 2: user_id 不匹配

**解决方法**:

方法 A: 添加和查询时使用相同的 user_id
```python
memory_tool = MemoryTool(user_id="same_user")
memory_tool.execute(action="add", content="...", memory_type="semantic")
memory_tool.execute(action="search", query="...")  # 默认使用初始化时的 user_id
```

方法 B: 查询时不指定 user_id
```python
result = memory_tool.execute(
    action="search",
    query="...",
    user_id=None  # 不过滤 user_id
)
```

### 问题 3: 环境变量未设置

**解决方法**: 确保在使用前设置环境变量

```bash
# 方法 1: 在命令行设置
export QDRANT_URL="your_url"
export QDRANT_API_KEY="your_key"

# 方法 2: 在代码中设置
import os
os.environ['QDRANT_URL'] = "your_url"
os.environ['QDRANT_API_KEY'] = "your_key"
```

## 文件变更清单

| 文件 | 变更类型 | 描述 |
|------|---------|------|
| `memory/types/semantic.py` | 修改 | 添加详细的向量搜索调试日志 |
| `memory/types/semantic.py` | 修改 | 添加 retrieve 方法的 debug 参数支持 |
| `tools/builtin/memory_tool.py` | 修改 | 改进搜索失败时的错误提示 |
| `demo/diagnose_memory.py` | 新建 | 记忆系统诊断脚本 |
| `demo/test_memory_retrieve.py` | 新建 | 简化的测试脚本 |
| `MEMORY_DEBUG_GUIDE.md` | 新建 | 本文档 |

## 验证

运行测试脚本验证修复：

```bash
python demo/test_memory_retrieve.py
```

预期输出：
```
添加结果: ✅ 记忆已添加 (ID: xxx...)
检索结果:
🔍 找到 1 条相关记忆:
1. [语义记忆] 测试内容：这是一条关于人工智能的记忆 (重要性: 0.80)
```
