# demo/memory_demo.py 代码执行调用链详解

## 目录

1. [初始化阶段](#初始化阶段)
2. [测试用例1: 添加语义记忆 - 山河剑心](#测试用例1-添加语义记忆---山河剑心)
3. [测试用例2: 添加语义记忆 - 秋叶悲歌](#测试用例2-添加语义记忆---秋叶悲歌)
4. [测试用例3: 添加语义记忆 - 春华秋实](#测试用例3-添加语义记忆---春华秋实)
5. [测试用例4: 搜索特定记忆](#测试用例4-搜索特定记忆)
6. [测试用例5: 获取记忆摘要](#测试用例5-获取记忆摘要)

---

## 初始化阶段

### 代码行: 3-18

```python
from tiny_agents.tools.builtin.memory_tool import MemoryTool
from tiny_agents.agents.simple_agent import SimpleAgent
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.tools.registry import ToolRegistry

llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="Memory Agent",
    llm=llm,
    system_prompt="你是一个拥有记忆能力的AI助手."
)

memory_tool = MemoryTool(user_id="user123")
tool_registry = ToolRegistry()
tool_registry.register_tool(memory_tool)
agent.tool_registry = tool_registry
```

### 初始化调用链

```
┌─────────────────────────────────────────────────────────────────────┐
│                          初始化阶段                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 1. HelloAgentsLLM()                                                 │
│    └── core/llm.py:HelloAgentsLLM.__init__()                        │
│        └── 初始化 LLM 配置                                           │
│                                                                     │
│ 2. SimpleAgent(name, llm, system_prompt)                            │
│    └── agents/simple_agent.py:SimpleAgent.__init__()                │
│        ├── 保存 name, llm, system_prompt                           │
│        └── 初始化 tool_registry = None                              │
│                                                                     │
│ 3. MemoryTool(user_id="user123")                                    │
│    └── tools/builtin/memory_tool.py:MemoryTool.__init__()           │
│        ├── self.memory_config = MemoryConfig()                      │
│        ├── self.memory_types = ["working", "episodic", "semantic"]  │
│        └── self.memory_manager = MemoryManager(...)                 │
│            └── memory/manager.py:MemoryManager.__init__()            │
│                ├── self.config = MemoryConfig()                     │
│                ├── self.user_id = "user123"                         │
│                └── 初始化各类型记忆:                                 │
│                    ├── self.memory_types['working'] = WorkingMemory │
│                    ├── self.memory_types['episodic'] = EpisodicMemory│
│                    └── self.memory_types['semantic'] = SemanticMemory│
│                        └── memory/types/semantic.py:SemanticMemory.__init__()
│                            ├── self.embedding_model = get_text_embedder()
│                            │   └── memory/embedding.py:get_text_embedder()
│                            │       └── 初始化 sentence-transformers 模型
│                            ├── self.vector_store = QdrantConnectionManager.get_instance()
│                            │   └── memory/storage/qdrant_store.py:QdrantConnectionManager.get_instance()
│                            │       └── memory/storage/qdrant_store.py:QdrantVectorStore.__init__()
│                            │           ├── self.client = QdrantClient(url, api_key)
│                            │           └── self._ensure_collection()
│                            │               └── 创建/获取 tiny_agents_vectors 集合
│                            ├── self.graph_store = Neo4jGraphStore()
│                            │   └── memory/storage/neo4j_store.py:Neo4jGraphStore.__init__()
│                            │       └── 连接 Neo4j 图数据库
│                            └── self.semantic_memories = []
│                                                                     │
│ 4. ToolRegistry()                                                   │
│    └── tools/registry.py:ToolRegistry.__init__()                    │
│        └── self.tools = {}                                          │
│                                                                     │
│ 5. tool_registry.register_tool(memory_tool)                         │
│    └── tools/registry.py:ToolRegistry.register_tool()               │
│        └── self.tools["memory"] = memory_tool                       │
│                                                                     │
│ 6. agent.tool_registry = tool_registry                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 测试用例1: 添加语义记忆 - 山河剑心

### 代码行: 20-27

```python
print("第一次对话:")
result = memory_tool.execute(
    action="add",
    content="我的名字是山河剑心，是一名人工智能爱好者，专注于LLM和AI相关技术。 我喜欢学习和分享人工智能的最新发展。",
    memory_type="semantic",
    importance=0.8
)
print("Agent Response:", result)
```

### 完整调用链

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    memory_tool.execute(action="add", ...)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ memory_tool.execute(action="add", content="...", memory_type="semantic")    │
│   │                                                                         │
│   └─> tools/builtin/memory_tool.py:MemoryTool.execute()                    │
│       │                                                                     │
│       ├── action == "add" → return self._add_memory(...)                    │
│       │                                                                     │
│       └─> _add_memory(content, memory_type="semantic", importance=0.8)     │
│           │                                                                 │
│           ├── 生成 session_id: "session_20260310_HHMMSS"                    │
│           │                                                                 │
│           ├── 更新 metadata:                                                │
│           │   {                                                             │
│           │     "session_id": "session_20260310_...",                       │
│           │     "timestamp": "2026-03-10T10:30:35.123456"                   │
│           │   }                                                             │
│           │                                                                 │
│           └─> self.memory_manager.add_memory(                              │
│                   content="我的名字是山河剑心...",                           │
│                   memory_type="semantic",                                  │
│                   importance=0.8,                                          │
│                   metadata={...},                                          │
│                   auto_classify=False                                      │
│               )                                                             │
│               │                                                             │
│               └─> memory/manager.py:MemoryManager.add_memory()              │
│                   │                                                         │
│                   ├── auto_classify=False → 跳过自动分类                    │
│                   │                                                         │
│                   ├── importance 已提供 → 跳过计算                          │
│                   │                                                         │
│                   ├── 创建 MemoryItem:                                      │
│                   │   memory_item = MemoryItem(                             │
│                   │       id=str(uuid.uuid4()),     # 如 "b8a9514b-..."     │
│                   │       content="我的名字是山河剑心...",                   │
│                   │       memory_type="semantic",                           │
│                   │       user_id="user123",                               │
│                   │       timestamp=datetime.now(),                         │
│                   │       importance=0.8,                                   │
│                   │       metadata={...}                                    │
│                   │   )                                                     │
│                   │                                                         │
│                   └─> self.memory_types["semantic"].add(memory_item)        │
│                       │                                                     │
│                       └─> memory/types/semantic.py:SemanticMemory.add()     │
│                           │                                                 │
│                           ├── 1️⃣ 生成文本嵌入:                              │
│                           │   embedding = self.embedding_model.encode(content)│
│                           │   │                                             │
│                           │   └─> sentence-transformers 编码                 │
│                           │       └── 返回 384 维向量                       │
│                           │                                                 │
│                           ├── 2️⃣ 提取实体:                                  │
│                           │   entities = self._extract_entities(content)    │
│                           │   │                                             │
│                           │   └─> memory/types/semantic.py:_extract_entities()│
│                           │       │                                         │
│                           │       ├── spaCy NLP 处理:                       │
│                           │       │   self.nlp(content)                     │
│                           │       │   └── 提取: 山河剑心(PERSON), 人工智能等 │
│                           │       │                                         │
│                           │       ├── 规则补充提取 (不足5个时):              │
│                           │       │   └── 关键词提取补充                   │
│                           │       │                                         │
│                           │       └── 返回: [Entity(...), ...]              │
│                           │                                                 │
│                           ├── 3️⃣ 提取关系:                                  │
│                           │   relations = self._extract_relations(content, entities)│
│                           │   │                                             │
│                           │   └─> 基于 spaCy 依存分析提取关系               │
│                           │       └── 返回: [Relation(...), ...]            │
│                           │                                                 │
│                           ├── 4️⃣ 存储到 Neo4j 图数据库:                      │
│                           │   for entity in entities:                       │
│                           │       self._add_entity_to_graph(entity, memory_item)│
│                           │       │                                         │
│                           │       └─> memory/storage/neo4j_store.py:         │
│                           │           add_entity(entity, memory_id)         │
│                           │               └── Neo4j MERGE 语句              │
│                           │                                                 │
│                           │   for relation in relations:                    │
│                           │       self._add_relation_to_graph(relation, memory_item)│
│                           │       │                                         │
│                           │       └─> memory/storage/neo4j_store.py:         │
│                           │           add_relation(relation)                │
│                           │               └── Neo4j MERGE 关系              │
│                           │                                                 │
│                           ├── 5️⃣ 存储到 Qdrant 向量数据库:                    │
│                           │   metadata = {                                  │
│                           │       "memory_id": memory_item.id,              │
│                           │       "user_id": "user123",                     │
│                           │       "content": "我的名字是山河剑心...",        │
│                           │       "memory_type": "semantic",                │
│                           │       "timestamp": 16784...,                    │
│                           │       "importance": 0.8,                        │
│                           │       "entities": ["entity_1", "entity_2", ...], │
│                           │       "entity_count": N,                        │
│                           │       "relation_count": M                       │
│                           │   }                                             │
│                           │                                                 │
│                           │   success = self.vector_store.add_vectors(      │
│                           │       vectors=[embedding.tolist()],  # [[0.1, 0.2, ..., 0.3]]│
│                           │       metadata=[metadata],                      │
│                           │       ids=[memory_item.id]                      │
│                           │   )                                             │
│                           │   │                                             │
│                           │   └─> memory/storage/qdrant_store.py:           │
│                           │       QdrantVectorStore.add_vectors()           │
│                           │           │                                     │
│                           │           ├── 构建点数据:                        │
│                           │           │   points = [PointStruct(            │
│                           │           │       id=memory_item.id,             │
│                           │           │       vector=embedding,              │
│                           │           │       payload=metadata               │
│                           │           │   )]                                │
│                           │           │                                     │
│                           │           └── self.client.upsert(               │
│                           │                   collection_name="tiny_agents_vectors",│
│                           │                   points=points                  │
│                           │               )                                 │
│                           │               └── Qdrant HTTP API 调用           │
│                           │                                                 │
│                           ├── 6️⃣ 添加到本地缓存:                            │
│                           │   self.semantic_memories.append(memory_item)    │
│                           │                                                 │
│                           └── return memory_item.id                         │
│                               │                                             │
│                   ←── 返回 memory_id (如 "b8a9514b-8d3f-4a2e-9c1f-7d8e5f6a4b2c")│
│                   │                                                             │
│               ←── 返回 memory_id                                                 │
│               │                                                                 │
│           ←── 返回 f"✅ 记忆已添加 (ID: {memory_id[:8]}...)"                     │
│           │                                                                     │
│       ←── return result                                                         │
│                                                                             │
│←── print("Agent Response:", "✅ 记忆已添加 (ID: b8a9514b...)")                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 数据流图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        添加语义记忆数据流                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  输入: content = "我的名字是山河剑心，是一名人工智能爱好者..."           │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  1. 文本嵌入 (sentence-transformers)                             │    │
│  │     输入: "我的名字是山河剑心..."                                 │    │
│  │     输出: [0.1, -0.2, 0.3, ..., 0.4]  (384维向量)                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  2. 实体提取 (spaCy + 规则)                                      │    │
│  │     输入: "我的名字是山河剑心，是一名人工智能爱好者..."           │    │
│  │     输出: [                                                      │    │
│  │            Entity("山河剑心", "PERSON"),                          │    │
│  │            Entity("人工智能", "CONCEPT"),                         │    │
│  │            Entity("LLM", "CONCEPT"),                              │    │
│  │            Entity("AI", "CONCEPT"),                               │    │
│  │            Entity("技术", "CONCEPT")                              │    │
│  │          ]                                                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  3. 关系提取 (依存分析)                                          │    │
│  │     输入: content + entities                                     │    │
│  │     输出: [                                                      │    │
│  │            Relation("山河剑心", "IS_A", "爱好者"),               │    │
│  │            Relation("爱好者", "INTERESTED_IN", "人工智能"),       │    │
│  │            ...                                                   │    │
│  │          ]                                                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│                              ├──→ Neo4j 图数据库                        │
│                              │    MERGE (Entity:Entity {id: ...})     │
│                              │    MERGE (:Entity)-[:RELATION]->(:Entity)│
│                              │                                          │
│                              ├──→ Qdrant 向量数据库                     │
│                              ↓    PointStruct {                        │
│  ┌────────────────────────────────  id: uuid,                         │
│  │  4. 构建向量存储数据        vector: [0.1, -0.2, ...],            │
│  │     metadata = {            payload: {                             │
│  │       "memory_id": uuid,      "memory_id": uuid,                  │
│  │       "user_id": "user123",   "user_id": "user123",               │
│  │       "content": "...",       "content": "...",                    │
│  │       "memory_type": "...",   "memory_type": "semantic",          │
│  │       "timestamp": 16784...,  "timestamp": 16784...,              │
│  │       "importance": 0.8,      "importance": 0.8,                  │
│  │       "entities": [...],      "entities": [...],                  │
│  │       "entity_count": N,      "entity_count": N,                  │
│  │       "relation_count": M    "relation_count": M                  │
│  │     }                       }                                     │
│  │   }                         }                                     │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│                    Qdrant upsert(collection, points)                    │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  5. 本地缓存                                                       │    │
│  │     self.semantic_memories.append(MemoryItem)                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  输出: "✅ 记忆已添加 (ID: b8a9514b...)"                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 测试用例2: 添加语义记忆 - 秋叶悲歌

### 代码行: 30-37

```python
print("第二次对话:")
result2 = memory_tool.execute(
    action="add",
    content="我的名字是秋叶悲歌，是一名内容创作者，专注于短视频制作。 我喜欢分享最新的短视频制作技巧和经验。",
    memory_type="semantic",
    importance=0.7
)
print("Agent Response:", result2)
```

### 调用链

与测试用例1相同，只是输入内容不同：

```
memory_tool.execute(action="add", ...)
  └─> _add_memory(content="我的名字是秋叶悲歌...", importance=0.7)
      └─> memory_manager.add_memory(memory_type="semantic", importance=0.7)
          └─> SemanticMemory.add(memory_item)
              ├── 生成嵌入: content → 384维向量
              ├── 提取实体: 秋叶悲歌(PERSON), 内容创作者, 短视频, 制作...
              ├── 提取关系: 秋叶悲歌-IS_A-创作者, 创作者-FOCUSED_ON-短视频...
              ├── 存储到 Neo4j: 添加实体和关系
              ├── 存储到 Qdrant: upsert 向量点
              └── 本地缓存: semantic_memories.append()
```

---

## 测试用例3: 添加语义记忆 - 春华秋实

### 代码行: 39-46

```python
print("第三次对话:")
result3 = memory_tool.execute(
    action="add",
    content="我的名字是春华秋实，是一名产品经理，专注于产品设计和用户体验。",
    memory_type="semantic",
    importance=0.6
)
print("Agent Response:", result3)
```

### 调用链

与测试用例1、2相同，只是输入内容不同。

---

## 测试用例4: 搜索特定记忆

### 代码行: 48-52

```python
print("\n=== 搜索特定记忆 ===")
print("🔍 搜索 '人工智能':")
result = memory_tool.execute("query_points", query="人工智能", limit=3, user_id="user123")
print(result)
```

### 完整调用链

```
┌─────────────────────────────────────────────────────────────────────────────┐
│            memory_tool.execute(action="query_points", query="人工智能")      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ memory_tool.execute(action="query_points", query="人工智能", limit=3)       │
│   │                                                                         │
│   └─> tools/builtin/memory_tool.py:MemoryTool.execute()                    │
│       │                                                                     │
│       ├── action == "query_points" → return self._search_memory(...)        │
│       │                                                                     │
│       └─> _search_memory(query="人工智能", limit=3, user_id="user123")     │
│           │                                                                 │
│           ├── 处理 memory_type: memory_types = None (未指定)                │
│           │                                                                 │
│           └─> self.memory_manager.retrieve_memories(                        │
│                   query="人工智能",                                         │
│                   limit=3,                                                 │
│                   memory_types=None,  # 从所有类型检索                      │
│                   min_importance=0.1,                                      │
│                   user_id="user123"                                        │
│               )                                                             │
│               │                                                             │
│               └─> memory/manager.py:MemoryManager.retrieve_memories()       │
│                   │                                                         │
│                   ├── target_user_id = "user123"                            │
│                   ├── memory_types = ["working", "episodic", "semantic"]    │
│                   ├── per_type_limit = max(1, 3 // 3) = 1                   │
│                   │                                                         │
│                   └── for memory_type in ["working", "episodic", "semantic"]│
│                       │                                                     │
│                       ├── WorkingMemory.retrieve() → 返回 [] (无数据)       │
│                       ├── EpisodicMemory.retrieve() → 返回 [] (无数据)      │
│                       │                                                     │
│                       └─> SemanticMemory.retrieve(                         │
│                               query="人工智能",                             │
│                               limit=1,                                     │
│                               user_id="user123"                            │
│                           )                                                 │
│                           │                                                 │
│                           └─> memory/types/semantic.py:retrieve()          │
│                               │                                             │
│                               ├── 1️⃣ 向量检索:                              │
│                               │   vector_results = self._vector_search(    │
│                               │       query="人工智能",                      │
│                               │       limit=6,  # limit * 2                 │
│                               │       user_id="user123"                     │
│                               │   )                                         │
│                               │   │                                         │
│                               │   └─> _vector_search(query, limit, user_id) │
│                               │       │                                     │
│                               │       ├── 📊 DEBUG: 开始查询                │
│                               │       ├── 📊 DEBUG: 查询向量维度: 384        │
│                               │       ├── 📊 DEBUG: 过滤条件:               │
│                               │       │   {"memory_type": "semantic", "user_id": "user123"}│
│                               │       │                                     │
│                               │       ├── 生成查询向量:                      │
│                               │       │   query_embedding = encode("人工智能")│
│                               │       │   └── [0.2, 0.1, -0.3, ..., 0.5] (384维)│
│                               │       │                                     │
│                               │       ├── 📊 DEBUG: 集合信息: points=46, vector_size=384│
│                               │       │                                     │
│                               │       ├── Qdrant 向量检索:                  │
│                               │       │   results = self.vector_store.search_similar(│
│                               │       │       query_vector=query_embedding.tolist(),│
│                               │       │       limit=6,                                 │
│                               │       │       where={                                  │
│                               │       │           "memory_type": "semantic",           │
│                               │       │           "user_id": "user123"                 │
│                               │       │       }                                       │
│                               │       │   )                                           │
│                               │       │   │                                           │
│                               │       │   └─> memory/storage/qdrant_store.py:search_similar()│
│                               │       │       │                                       │
│                               │       │       ├── 构建 Filter:                       │
│                               │       │       │   Filter(must=[                       │
│                               │       │       │     FieldCondition(key="memory_type", match="semantic"),│
│                               │       │       │     FieldCondition(key="user_id", match="user123")│
│                               │       │       │   ])                                 │
│                               │       │       │                                       │
│                               │       │       ├── self.client.query_points(          │
│                               │       │       │       collection_name="tiny_agents_vectors",│
│                               │       │       │       query=query_vector,             │
│                               │       │       │       query_filter=Filter,            │
│                               │       │       │       limit=6                         │
│                               │       │       │   )                                   │
│                               │       │       │   └── Qdrant HTTP API                  │
│                               │       │       │       └── 返回相似度最高的6个点         │
│                               │       │       │                                         │
│                               │       │       ├── 📊 DEBUG: Qdrant原始返回 6 个结果   │
│                               │       │       │                                         │
│                               │       │       └── 转换格式:                            │
│                               │       │           for result in results:               │
│                               │       │               formatted_result = {             │
│                               │       │                   "id": result.id,             │
│                               │       │                   "score": result.score,        │
│                               │       │                   **result.payload  # 展开所有metadata│
│                               │       │               }                                │
│                               │       │           # formatted_result 包含:             │
│                               │       │           # - memory_id, user_id, content      │
│                               │       │           # - memory_type, timestamp, importance│
│                               │       │           # - entities, entity_count...         │
│                               │       │                                               │
│                               │       └── 📊 DEBUG: 完成查询: 返回 6 个格式化结果     │
│                               │                                                 │
│                               ├── 2️⃣ 图检索:                                   │
│                               │   graph_results = self._graph_search(            │
│                               │       query="人工智能",                           │
│                               │       limit=6,                                   │
│                               │       user_id="user123"                          │
│                               │   )                                             │
│                               │   │                                             │
│                               │   └─> _graph_search(query, limit, user_id)       │
│                               │       │                                         │
│                               │       ├── 提取查询实体:                          │
│                               │       │   query_entities = _extract_entities("人工智能")│
│                               │       │   └── [Entity("人工智能", "CONCEPT")]     │
│                               │       │                                         │
│                               │       ├── 在 Neo4j 中查找相关实体:               │
│                               │       │   related_entities = self.graph_store.find_related_entities(│
│                               │       │       entity_id="人工智能的entity_id",     │
│                               │       │       max_depth=2,                         │
│                               │       │       limit=20                             │
│                               │       │   )                                       │
│                               │       │   └── Neo4j Cypher 查询                   │
│                               │       │                                         │
│                               │       └── 📊 DEBUG: Neo4j图搜索返回 N 个结果      │
│                               │                                                 │
│                               ├── 3️⃣ 混合排序:                                  │
│                               │   combined_results = self._combine_and_rank_results(│
│                               │       vector_results, graph_results, query, limit│
│                               │   )                                             │
│                               │   │                                             │
│                               │   └─> _combine_and_rank_results()               │
│                               │       │                                         │
│                               │       ├── 合并向量和图结果，按内容去重           │
│                               │       │   combined = {}                           │
│                               │       │   for result in vector_results:          │
│                               │       │       combined[memory_id] = {            │
│                               │       │           **result,                       │
│                               │       │           "vector_score": result["score"],│
│                               │       │           "graph_score": 0.0              │
│                               │       │       }                                   │
│                               │       │   for result in graph_results:            │
│                               │       │       if memory_id in combined:          │
│                               │       │           combined[memory_id]["graph_score"] = result["similarity"]│
│                               │       │                                         │
│                               │       ├── 计算混合分数:                           │
│                               │       │   for memory in combined:                │
│                               │       │       base_relevance = vector_score * 0.7 + graph_score * 0.3│
│                               │       │       importance_weight = 0.8 + (importance * 0.4)│
│                               │       │       combined_score = base_relevance * importance_weight│
│                               │       │                                         │
│                               │       └── 按分数排序返回                           │
│                               │                                                 │
│                               ├── 4️⃣ 过滤并转换:                                │
│                               │   for result in combined_results:               │
│                               │       memory_id = result["memory_id"]            │
│                               │       # 检查是否已遗忘                             │
│                               │       if memory.metadata.get("forgotten"):       │
│                               │           continue                               │
│                               │       # 构建 MemoryItem                          │
│                               │       memory_item = MemoryItem(                 │
│                               │           id=result["memory_id"],                │
│                               │           content=result["content"],              │
│                               │           memory_type="semantic",                 │
│                               │           user_id=result.get("user_id"),          │
│                               │           timestamp=...,                          │
│                               │           importance=result.get("importance"),    │
│                               │           metadata={                             │
│                               │               **result.get("metadata", {}),       │
│                               │               "combined_score": ...,              │
│                               │               "vector_score": ...,                │
│                               │               "graph_score": ...,                 │
│                               │               "probability": ...                   │
│                               │           }                                     │
│                               │       )                                          │
│                               │       result_memories.append(memory_item)        │
│                               │                                                 │
│                               └── 📊 INFO: 检索到 N 条相关记忆                   │
│                                   │                                             │
│                   ←── 返回 [MemoryItem, ...]  (所有类型的结果合并)              │
│                   │                                                             │
│                   ├── 按重要性排序: all_results.sort(key=lambda x: x.importance, reverse=True)│
│                   └── return all_results[:3]  # 只返回前3条                     │
│                                                                             │
│               ←── 返回 results: [MemoryItem, MemoryItem, ...]                 │
│               │                                                                 │
│           ←── 格式化结果:                                                      │
│               "🔍 找到 {len(results)} 条相关记忆:\n"                           │
│               "1. [语义记忆] 我的名字是山河剑心... (重要性: 0.80)\n"           │
│               ...                                                               │
│           │                                                                     │
│       ←── return formatted_result                                               │
│                                                                             │
│←── print(formatted_result)                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 检索数据流

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        检索语义记忆数据流                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  输入: query = "人工智能", limit = 3, user_id = "user123"              │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  1. 向量检索 (Qdrant)                                             │    │
│  │     query_embedding = encode("人工智能")                          │    │
│  │     └── [0.2, 0.1, -0.3, ..., 0.5] (384维向量)                   │    │
│  │                                                                  │    │
│  │     Qdrant.search_similar(                                       │    │
│  │         query_vector,                                            │    │
│  │         filter={                                                 │    │
│  │             "memory_type": "semantic",                           │    │
│  │             "user_id": "user123"                                 │    │
│  │         },                                                       │    │
│  │         limit=6                                                  │    │
│  │     )                                                            │    │
│  │     └── 返回: [                                                  │    │
│  │              {                                                    │    │
│  │                "id": "uuid-1",                                    │    │
│  │                "score": 0.85,  # 相似度                           │    │
│  │                "memory_id": "uuid-1",                             │    │
│  │                "user_id": "user123",                              │    │
│  │                "content": "我的名字是山河剑心，是一名人工智能爱好者...",│
│  │                "importance": 0.8,                                 │    │
│  │                "entities": ["entity_1", ...]                      │    │
│  │              },                                                   │    │
│  │              { "score": 0.72, ... },  # 第二条                    │    │
│  │              ...                                                 │    │
│  │            ]                                                     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  2. 图检索 (Neo4j)                                               │    │
│  │     query_entities = extract_entities("人工智能")                │    │
│  │     └── [Entity("人工智能", "CONCEPT")]                          │    │
│  │                                                                  │    │
│  │     Neo4j.find_related_entities(                                │    │
│  │         entity_id="人工智能的entity_id",                         │    │
│  │         max_depth=2                                             │    │
│  │     )                                                            │    │
│  │     └── Cypher: MATCH path = (e:Entity {id: $id})-[*1..2]-(related)│    │
│  │         RETURN related                                          │    │
│  │                                                                  │    │
│  │     返回: [                                                      │    │
│  │            {"memory_id": "uuid-1", "similarity": 0.6},           │    │
│  │            ...                                                   │    │
│  │          ]                                                      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  3. 混合排序                                                      │    │
│  │     合并 vector_results 和 graph_results                         │    │
│  │     按 memory_id 去重                                            │    │
│  │                                                                  │    │
│  │     计算混合分数:                                                 │    │
│  │     base_relevance = vector_score * 0.7 + graph_score * 0.3      │    │
│  │     importance_weight = 0.8 + (importance * 0.4)                 │    │
│  │     combined_score = base_relevance * importance_weight          │    │
│  │                                                                  │    │
│  │     按 combined_score 排序                                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  4. 过滤并转换                                                    │    │
│  │     跳过已遗忘的记忆                                              │    │
│  │     转换为 MemoryItem 对象                                        │    │
│  │     添加分数和概率信息到 metadata                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  输出: [MemoryItem, MemoryItem, ...]                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 测试用例5: 获取记忆摘要

### 代码行: 53-55

```python
print("\n=== 记忆摘要 ===")
result = memory_tool.execute("summary")
print(result)
```

### 完整调用链

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    memory_tool.execute(action="summary")                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ memory_tool.execute(action="summary")                                      │
│   │                                                                         │
│   └─> tools/builtin/memory_tool.py:MemoryTool.execute()                    │
│       │                                                                     │
│       ├── action == "summary" → return self._get_summary()                 │
│       │                                                                     │
│       └─> _get_summary(limit=10)                                           │
│           │                                                                 │
│           ├── 1️⃣ 获取统计信息:                                             │
│           │   stats = self.memory_manager.get_memory_stats()                │
│           │   │                                                             │
│           │   └─> memory/manager.py:get_memory_stats()                     │
│           │       │                                                         │
│           │       └── for memory_type, memory_instance in self.memory_types.items():│
│           │              type_stats = memory_instance.get_stats()           │
│           │              stats["memories_by_type"][memory_type] = type_stats│
│           │              stats["total_memories"] += type_stats.get("count", 0)│
│           │                                                                   │
│           ├── 2️⃣ 获取重要记忆:                                               │
│           │   important_memories = self.memory_manager.retrieve_memories(    │
│           │       query="",                                                │
│           │       memory_types=None,  # 从所有类型检索                      │
│           │       limit=30,  # limit * 3                                   │
│           │       min_importance=0.5                                       │
│           │   )                                                             │
│           │   │                                                             │
│           │   └─> memory/manager.py:retrieve_memories()                     │
│           │       └─> SemanticMemory.retrieve(query="", ...)               │
│           │           └─> _vector_search(query="", limit=60)               │
│           │               └─> Qdrant.search_similar()                      │
│           │                   └── 返回所有记忆（空查询返回所有）             │
│           │                                                                 │
│           ├── 3️⃣ 去重:                                                      │
│           │   seen_ids = set()                                             │
│           │   seen_contents = set()                                         │
│           │   unique_memories = []                                          │
│           │   for memory in important_memories:                             │
│           │       if memory.id in seen_ids: continue                        │
│           │       content_key = memory.content.strip().lower()              │
│           │       if content_key in seen_contents: continue                 │
│           │       seen_ids.add(memory.id)                                   │
│           │       seen_contents.add(content_key)                            │
│           │       unique_memories.append(memory)                            │
│           │                                                                 │
│           ├── 4️⃣ 按重要性排序:                                              │
│           │   unique_memories.sort(key=lambda x: x.importance, reverse=True)│
│           │                                                                 │
│           └── 5️⃣ 格式化输出:                                                │
│               return f"""                                                   │
│               📊 记忆系统摘要                                                │
│               总记忆数: {stats['total_memories']}                           │
│               当前会话: {self.current_session_id}                           │
│               对话轮次: {self.conversation_count}                            │
│                                                                         │
│               📋 记忆类型分布:                                                │
│                 • 工作记忆: X 条 (平均重要性: Y)                            │
│                 • 情景记忆: X 条 (平均重要性: Y)                            │
│                 • 语义记忆: X 条 (平均重要性: Y)                            │
│                                                                         │
│               ⭐ 重要记忆 (前10条):                                          │
│                 1. {content} (重要性: X.XX)                                 │
│                 ...                                                       │
│               """                                                           │
│                                                                             │
│       ←── return formatted_summary                                           │
│                                                                             │
│←── print(formatted_summary)                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 完整执行时序图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          memory_demo.py 执行时序                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  时间线                                                                      │
│    │                                                                         │
│    ├─ [00:00] 初始化: LLM, Agent, MemoryTool, ToolRegistry                  │
│    │                                                                         │
│    ├─ [00:01] 测试1: 添加记忆 "山河剑心"                                      │
│    │         ├─ MemoryTool.execute("add")                                   │
│    │         ├─ SemanticMemory.add()                                        │
│    │         ├─ encode() → 384维向量                                         │
│    │         ├─ extract_entities() → [山河剑心, 人工智能, LLM, AI, 技术]    │
│    │         ├─ extract_relations() → [IS_A, INTERESTED_IN, ...]            │
│    │         ├─ Neo4j.add_entity() → MERGE Entity                          │
│    │         ├─ Neo4j.add_relation() → MERGE Relation                      │
│    │         ├─ Qdrant.add_vectors() → upsert point                        │
│    │         └─ 输出: "✅ 记忆已添加 (ID: b8a9514b...)"                      │
│    │                                                                         │
│    ├─ [00:02] 测试2: 添加记忆 "秋叶悲歌"                                      │
│    │         └─ (流程同测试1)                                                 │
│    │                                                                         │
│    ├─ [00:03] 测试3: 添加记忆 "春华秋实"                                      │
│    │         └─ (流程同测试1)                                                 │
│    │                                                                         │
│    ├─ [00:04] 测试4: 搜索 "人工智能"                                          │
│    │         ├─ MemoryTool.execute("query_points")                          │
│    │         ├─ SemanticMemory.retrieve()                                   │
│    │         ├─ _vector_search()                                            │
│    │         │   ├─ encode("人工智能") → 查询向量                            │
│    │         │   ├─ Qdrant.search_similar(filter={user_id="user123"})       │
│    │         │   └─ 返回 6 个结果 (按相似度排序)                             │
│    │         ├─ _graph_search()                                             │
│    │         │   ├─ extract_entities("人工智能")                            │
│    │         │   └─ Neo4j.find_related_entities()                           │
│    │         ├─ _combine_and_rank_results()                                 │
│    │         │   └─ 混合分数 = 向量分*0.7 + 图分*0.3                        │
│    │         └─ 输出: "🔍 找到 1 条相关记忆..."                               │
│    │                                                                         │
│    └─ [00:05] 测试5: 获取摘要                                                 │
│              ├─ MemoryTool.execute("summary")                                │
│              ├─ get_memory_stats() → 统计各类型记忆数量                       │
│              ├─ retrieve_memories(query="") → 获取所有重要记忆                │
│              └─ 输出: 摘要信息（总数、分布、重要记忆列表）                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 数据库操作总结

### Qdrant 向量数据库操作

| 操作 | 方法 | 数据 | 调用位置 |
|------|------|------|---------|
| 添加向量 | `upsert()` | PointStruct {id, vector, payload} | `SemanticMemory.add()` |
| 搜索向量 | `query_points()` | query_vector + filter | `SemanticMemory._vector_search()` |

### Neo4j 图数据库操作

| 操作 | 方法 | 数据 | 调用位置 |
|------|------|------|---------|
| 添加实体 | `MERGE (e:Entity)` | Entity {id, name, type} | `SemanticMemory._add_entity_to_graph()` |
| 添加关系 | `MERGE (e1)-[r:REL]->(e2)` | Relation {from, to, type} | `SemanticMemory._add_relation_to_graph()` |
| 查找实体 | `MATCH (e:Entity)` | entity_id | `SemanticMemory._extract_entities()` |
| 查找相关实体 | `MATCH path=(e)-[*1..2]-(related)` | max_depth=2 | `SemanticMemory._graph_search()` |

---

## 关键数据结构

### MemoryItem

```python
MemoryItem {
    id: str,                    # UUID 如 "b8a9514b-8d3f-4a2e-9c1f-7d8e5f6a4b2c"
    content: str,               # 记忆内容
    memory_type: str,           # "working", "episodic", "semantic", "perceptual"
    user_id: str,               # 用户ID 如 "user123"
    timestamp: datetime,        # 创建时间
    importance: float,          # 重要性分数 0.0-1.0
    metadata: Dict[str, Any] {  # 元数据
        "session_id": str,
        "timestamp": str,
        "entities": List[str],  # 实体ID列表
        "relations": List[str], # 关系字符串列表
        "combined_score": float, # 检索时添加
        "vector_score": float,   # 检索时添加
        "graph_score": float,    # 检索时添加
        "probability": float     # 检索时添加
    }
}
```

### Qdrant Payload 结构

```python
payload {
    "memory_id": str,           # 记忆ID (与Point ID相同)
    "user_id": str,             # 用户ID
    "content": str,             # 记忆内容
    "memory_type": str,         # 记忆类型
    "timestamp": int,           # Unix时间戳
    "importance": float,        # 重要性分数
    "entities": List[str],      # 实体ID列表
    "entity_count": int,        # 实体数量
    "relation_count": int,      # 关系数量
    # ... 其他元数据
}
```

---

## 总结

`demo/memory_demo.py` 演示了完整的记忆系统功能：

1. **添加记忆** - 将文本转换为向量、实体、关系，分别存储到 Qdrant 和 Neo4j
2. **检索记忆** - 通过向量相似度和图关系混合检索，返回最相关的记忆
3. **记忆摘要** - 统计记忆系统状态，列出重要记忆

核心特点：
- **混合检索**: 向量检索 (Qdrant) + 图检索 (Neo4j)
- **多模态存储**: 向量数据库 (语义) + 图数据库 (关系) + 本地缓存 (快速访问)
- **智能排序**: 结合相似度、重要性、关系强度计算最终分数
