# demo/rag_demo.py 代码执行调用链详解

## 目录

1. [初始化阶段](#初始化阶段)
2. [测试用例1: 添加文本知识 - Python介绍](#测试用例1-添加文本知识---python介绍)
3. [测试用例2: 添加文本知识 - 机器学习基础](#测试用例2-添加文本知识---机器学习基础)
4. [测试用例3: 添加文本知识 - RAG概念](#测试用例3-添加文本知识---rag概念)
5. [测试用例4: 搜索知识](#测试用例4-搜索知识)
6. [测试用例5: 获取知识库统计](#测试用例5-获取知识库统计)

---

## 初始化阶段

### 代码行: 1-24

```python
from tiny_agents.tools.registry import ToolRegistry
from tiny_agents.tools.builtin.rag_tool import RAGTool
from tiny_agents.tools.builtin.memory_tool import MemoryTool
from tiny_agents.agents.simple_agent import SimpleAgent
from tiny_agents.core.llm import HelloAgentsLLM


llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="RAG Agent",
    llm=llm,
    system_prompt="你是一个知识检索能力的AI助手."
)

rag_tool = RAGTool(
    knowledge_base_path="./knowledge_base.json",
    collection_name="my_knowledge_collection",
    rag_namespace="my_rag_namespace"
)

tool_registry = ToolRegistry()
tool_registry.register_tool(rag_tool)
agent.tool_registry = tool_registry
```

### 初始化调用链

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          初始化阶段                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 1. HelloAgentsLLM()                                                         │
│    └── core/llm.py:HelloAgentsLLM.__init__()                                │
│        └── 初始化 LLM 配置 (默认使用 DeepSeek 或配置的模型)                  │
│                                                                             │
│ 2. SimpleAgent(name, llm, system_prompt)                                    │
│    └── agents/simple_agent.py:SimpleAgent.__init__()                        │
│        └── 保存 name, llm, system_prompt, tool_registry=None                │
│                                                                             │
│ 3. RAGTool(                                                                  │
│        knowledge_base_path="./knowledge_base.json",                          │
│        collection_name="my_knowledge_collection",                           │
│        rag_namespace="my_rag_namespace"                                     │
│    )                                                                         │
│    └── tools/builtin/rag_tool.py:RAGTool.__init__()                         │
│        │                                                                     │
│        ├── 保存配置参数                                                       │
│        ├── os.makedirs(knowledge_base_path, exist_ok=True)                  │
│        │                                                                     │
│        └─> self._init_components()                                          │
│            │                                                                 │
│            └─> create_rag_pipeline(                                        │
│                    qdrant_url=QDRANT_URL (from env),                       │
│                    qdrant_api_key=QDRANT_API_KEY (from env),               │
│                    collection_name="my_knowledge_collection",               │
│                    rag_namespace="my_rag_namespace"                         │
│                )                                                             │
│                │                                                             │
│                └─> memory/rag/pipeline.py:create_rag_pipeline()            │
│                    │                                                         │
│                    ├── dimension = get_dimension(384)  # 向量维度           │
│                    │                                                         │
│                    ├── store = QdrantVectorStore(                           │
│                    │       url=qdrant_url,                                  │
│                    │       api_key=qdrant_api_key,                          │
│                    │       collection_name="my_knowledge_collection",       │
│                    │       vector_size=384,                                 │
│                    │       distance="cosine"                               │
│                    │   )                                                     │
│                    │   │                                                     │
│                    │   └─> memory/storage/qdrant_store.py:                 │
│                    │       QdrantVectorStore.__init__()                     │
│                    │           │                                             │
│                    │           ├── self.client = QdrantClient(url, api_key) │
│                    │           │   └── 连接到 Qdrant 云服务                 │
│                    │           │                                             │
│                    │           └─> self._ensure_collection()                │
│                    │               │                                         │
│                    │               └── 检查/创建集合:                        │
│                    │                   my_knowledge_collection                │
│                    │                   vectors_config: size=384, distance=cosine│
│                    │                                                           │
│                    ├── 定义 add_documents 函数:                               │
│                    │   └─> load_and_chunk_texts(paths, chunk_size, overlap) │
│                    │       └─> index_chunks(store, chunks, namespace)      │
│                    │                                                           │
│                    ├── 定义 search 函数:                                      │
│                    │   └─> search_vectors(store, query, top_k, namespace)   │
│                    │                                                           │
│                    ├── 定义 search_advanced 函数:                             │
│                    │   └─> search_vectors_expanded(...)                     │
│                    │                                                           │
│                    ├── 定义 get_stats 函数:                                   │
│                    │   └─> store.get_collection_stats()                    │
│                    │                                                           │
│                    └── return {                                              │
│                           "store": store,                                    │
│                           "namespace": "my_rag_namespace",                   │
│                           "add_documents": add_documents,                   │
│                           "search": search,                                 │
│                           "search_advanced": search_advanced,               │
│                           "get_stats": get_stats                            │
│                       }                                                     │
│                    │                                                         │
│                ←── 返回 pipeline 字典                                        │
│                │                                                             │
│            └── self._pipelines["my_rag_namespace"] = pipeline               │
│                                                                             │
│        ├── self.llm = HelloAgentsLLM()  # 用于问答生成                      │
│        └── print("✅ RAG工具初始化成功: namespace=my_rag_namespace, ...")   │
│                                                                             │
│ 4. ToolRegistry() + register_tool(rag_tool)                                 │
│    └── tools/registry.py:ToolRegistry.register_tool()                       │
│        └── self.tools["rag"] = rag_tool                                     │
│                                                                             │
│ 5. agent.tool_registry = tool_registry                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 测试用例1: 添加文本知识 - Python介绍

### 代码行: 26-32

```python
# 添加第一个知识
result1 = rag_tool.execute(
    "add_text",
    text="Python是一种高级编程语言，由Guido van Rossum于1991年首次发布。Python的设计哲学强调代码的可读性和简洁的语法。",
    document_id="python_intro"
)
print(f"知识1: {result1}")
```

### 完整调用链

```
┌─────────────────────────────────────────────────────────────────────────────┐
│            rag_tool.execute(action="add_text", text="...", document_id="...")│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ rag_tool.execute(action="add_text", text="...", document_id="python_intro") │
│   │                                                                         │
│   └─> tools/builtin/rag_tool.py:RAGTool.execute()                         │
│       │                                                                     │
│       ├── action == "add_text" → return self._add_text(...)                │
│       │                                                                     │
│       └─> _add_text(                                                        │
│               text="Python是一种高级编程语言...",                            │
│               document_id="python_intro",                                   │
│               chunk_size=800,                                              │
│               chunk_overlap=100                                            │
│           )                                                                 │
│           │                                                                 │
│           ├── 验证: text 不为空                                            │
│           │                                                                 │
│           ├── 创建临时文件:                                                │
│           │   tmp_path = "./knowledge_base.json/python_intro.md"             │
│           │   with open(tmp_path, 'w') as f:                                │
│           │       f.write(text)                                             │
│           │                                                                 │
│           └─> pipeline["add_documents"]([tmp_path], chunk_size, overlap)    │
│               │                                                             │
│               └─> memory/rag/pipeline.py:add_documents()                    │
│                   │                                                         │
│                   └─> chunks = load_and_chunk_texts(                       │
│                           paths=[tmp_path],                                │
│                           chunk_size=800,                                  │
│                           chunk_overlap=100,                                │
│                           namespace="my_rag_namespace",                      │
│                           source_label="rag"                                │
│                       )                                                     │
│                       │                                                     │
│                       └─> memory/rag/pipeline.py:load_and_chunk_texts()    │
│                           │                                                 │
│                           ├── 1️⃣ 读取并转换文档:                            │
│                           │   markdown_text = _convert_to_markdown(path)    │
│                           │   │                                             │
│                           │   └─> _convert_to_markdown()                   │
│                           │       │                                         │
│                           │       ├── 检查扩展名: .md                        │
│                           │       │                                         │
│                           │       └─> _fallback_text_reader(path)           │
│                           │           │                                     │
│                           │           └─> 读取文件内容                       │
│                           │               with open(path, 'r', encoding='utf-8')│
│                           │               └── 返回 markdown_text              │
│                           │                                                 │
│                           ├── 2️⃣ 检测语言:                                 │
│                           │   lang = _detect_lang(markdown_text)           │
│                           │   └── 使用 langdetect 检测 → "zh" (中文)       │
│                           │                                                 │
│                           ├── 3️⃣ 生成文档ID:                               │
│                           │   doc_id = md5(f"{path}|{len(text)}")          │
│                           │   └── 如 "a1b2c3d4e5f6..."                       │
│                           │                                                 │
│                           ├── 4️⃣ 分割段落:                                  │
│                           │   paragraphs = _split_paragraphs_with_headings()│
│                           │   └── 按标题层级组织段落                         │
│                           │       [                                         │
│                           │         {content: "Python是一种高级编程语言...", heading_path: None},│
│                           │         ...                                      │
│                           │       ]                                         │
│                           │                                                 │
│                           ├── 5️⃣ 分块处理:                                  │
│                           │   chunks = _chunk_paragraphs(paragraphs, 800, 100)│
│                           │   └── 将段落按 token 数分块，带重叠              │
│                           │       [                                         │
│                           │         {                                        │
│                           │           content: "Python是一种高级编程语言，由Guido van Rossum...",│
│                           │           start: 0,                               │
│                           │           end: 150,                               │
│                           │           heading_path: None                      │
│                           │         },                                        │
│                           │         ... (通常1-2个chunk，因为文本较短)      │
│                           │       ]                                         │
│                           │                                                 │
│                           ├── 6️⃣ 生成 chunk 唯一ID:                        │
│                           │   for each chunk:                               │
│                           │       chunk_id = f"{doc_id}_chunk_{i}"           │
│                           │       content_hash = md5(content)                │
│                           │                                                 │
│                           └── 7️⃣ 构建返回结构:                            │
│                               chunks.append({                               │
│                                   "id": chunk_id,                          │
│                                   "content": chunk_content,                 │
│                                   "metadata": {                            │
│                                       "source_path": path,                  │
│                                       "file_ext": ".md",                    │
│                                       "doc_id": doc_id,                     │
│                                       "lang": "zh",                         │
│                                       "start": 0,                           │
│                                       "end": 150,                           │
│                                       "content_hash": hash,                 │
│                                       "namespace": "my_rag_namespace",       │
│                                       "source": "rag",                      │
│                                       "external": True,                     │
│                                       "heading_path": None,                 │
│                                       "format": "markdown"                  │
│                                   }                                        │
│                               })                                            │
│                                                                             │
│                   ←── 返回 chunks (通常1-2个)                               │
│                   │                                                             │
│                   └─> index_chunks(                                          │
│                           store=store,                                      │
│                           chunks=chunks,                                     │
│                           rag_namespace="my_rag_namespace"                   │
│                       )                                                     │
│                       │                                                     │
│                       └─> memory/rag/pipeline.py:index_chunks()             │
│                           │                                                 │
│                           ├── 1️⃣ 获取嵌入模型:                             │
│                           │   embedder = get_text_embedder()                │
│                           │   └── 返回 sentence-transformers 模型            │
│                           │                                                 │
│                           ├── 2️⃣ 预处理文本:                                │
│                           │   for each chunk:                               │
│                           │       processed = _preprocess_markdown_for_embedding()│
│                           │       └── 移除 markdown 标记，保留语义内容     │
│                           │                                                 │
│                           ├── 3️⃣ 批量编码:                                  │
│                           │   for i in range(0, len(chunks), batch_size=64):│
│                           │       part_vecs = embedder.encode(texts)        │
│                           │       └── 返回 [[0.1, 0.2, ...], [0.3, 0.4, ...]]│
│                           │           (384维向量列表)                        │
│                           │                                                 │
│                           ├── 4️⃣ 构建 payload:                             │
│                           │   for chunk, vec in zip(chunks, vecs):         │
│                           │       payload = {                                │
│                           │           "memory_type": "rag_chunk",            │
│                           │           "is_rag_data": True,                   │
│                           │           "data_source": "rag_pipeline",         │
│                           │           "rag_namespace": "my_rag_namespace",   │
│                           │           "memory_id": chunk["id"],              │
│                           │           "content": chunk["content"],            │
│                           │           **chunk["metadata"]                   │
│                           │       }                                         │
│                           │                                                 │
│                           └── 5️⃣ 存储到 Qdrant:                           │
│                               store.add_vectors(                            │
│                                   vectors=vecs,                             │
│                                   metadata=payloads,                        │
│                                   ids=chunk_ids                             │
│                               )                                             │
│                               │                                             │
│                               └─> QdrantVectorStore.add_vectors()          │
│                                   └─> self.client.upsert(                   │
│                                           collection_name="my_knowledge_collection",│
│                                           points=[PointStruct{               │
│                                               id=chunk_id,                 │
│                                               vector=vec,                  │
│                                               payload=payload              │
│                                           }]                               │
│                                       )                                     │
│                                       └── HTTP API 调用                     │
│                                                                             │
│               ←── 返回 len(chunks) (如 1)                                  │
│               │                                                             │
│           ├── 计算处理时间: process_ms = int((t1 - t0) * 1000)             │
│           │                                                                 │
│           ├── 清理临时文件: os.remove(tmp_path)                              │
│           │                                                                 │
│           └── 返回结果:                                                      │
│               """                                                              │
│               ✅ 文本已添加到知识库: python_intro                            │
│               📊 分块数量: 1                                                │
│               ⏱️ 处理时间: 250ms                                            │
│               📝 命名空间: my_rag_namespace                                 │
│               """                                                              │
│           │                                                                 │
│       ←── return result_string                                               │
│                                                                             │
│←── print(f"知识1: {result1}")                                              │
│     输出: 知识1: ✅ 文本已添加到知识库: python_intro                       │
│           📊 分块数量: 1                                                   │
│           ⏱️ 处理时间: 250ms                                               │
│           📝 命名空间: my_rag_namespace                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 数据流图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   添加文本知识到 RAG 系统数据流                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  输入: text = "Python是一种高级编程语言，由Guido van Rossum于1991年..." │
│        document_id = "python_intro"                                     │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  1. 创建临时文件                                                  │    │
│  │     ./knowledge_base.json/python_intro.md                        │    │
│  │     └── 写入文本内容                                              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  2. 文档解析 (load_and_chunk_texts)                             │    │
│  │     读取文件 → Markdown 文本                                       │    │
│  │     检测语言 → zh (中文)                                          │    │
│  │     生成 doc_id → MD5(path + len)                                │    │
│  │     分割段落 → 按标题层级                                          │    │
│  │     分块处理 → chunk_size=800, overlap=100                        │    │
│  │     └── 通常生成 1-2 个 chunk (文本较短)                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  3. 文本嵌入 (index_chunks)                                      │    │
│  │     预处理: 移除 markdown 标记                                     │    │
│  │     嵌入: sentence-transformers                                   │    │
│  │     输入: "Python是一种高级编程语言..."                           │    │
│  │     输出: [0.1, -0.2, 0.3, ..., 0.4] (384维向量)                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  4. 构建 Payload                                                 │    │
│  │     {                                                            │    │
│  │       "memory_type": "rag_chunk",                                │    │
│  │       "is_rag_data": true,                                       │    │
│  │       "data_source": "rag_pipeline",                             │    │
│  │       "rag_namespace": "my_rag_namespace",                       │    │
│  │       "memory_id": "a1b2c3d4_chunk_0",                          │    │
│  │       "content": "Python是一种高级编程语言...",                    │    │
│  │       "source_path": ".../python_intro.md",                       │    │
│  │       "doc_id": "a1b2c3d4e5f6...",                               │    │
│  │       "lang": "zh",                                              │    │
│  │       "format": "markdown"                                        │    │
│  │     }                                                            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│                    Qdrant.upsert(collection, points)                    │
│                    └── PointStruct {id, vector, payload}              │
│                                                                         │
│  输出: "✅ 文本已添加到知识库: python_intro                             │
│        "📊 分块数量: 1"                                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 测试用例2: 添加文本知识 - 机器学习基础

### 代码行: 34-40

```python
# 添加第二个知识
result2 = rag_tool.execute(
    "add_text",
    text="机器学习是人工智能的一个分支，通过算法让计算机从数据中学习模式。主要包括监督学习、无监督学习和强化学习三种类型。",
    document_id="ml_basics"
)
print(f"知识2: {result2}")
```

### 调用链

与测试用例1相同，只是输入内容不同：

```
rag_tool.execute(action="add_text", text="机器学习是...", document_id="ml_basics")
  └─> _add_text(text="机器学习是...", document_id="ml_basics")
      └─> 创建临时文件: ./knowledge_base.json/ml_basics.md
      └─> load_and_chunk_texts([tmp_path])
      └─> 解析 → 生成 1 个 chunk
      └─> index_chunks()
      └─> 嵌入 → Qdrant 存储
```

---

## 测试用例3: 添加文本知识 - RAG概念

### 代码行: 42-48

```python
# 添加第三个知识
result3 = rag_tool.execute(
    "add_text",
    text = "RAG（检索增强生成）是一种结合信息检索和文本生成的AI技术。它通过检索相关知识来增强大语言模型的生成能力。",
    document_id="rag_concept"
)
print(f"知识3: {result3}")
```

### 调用链

与测试用例1、2相同。

---

## 测试用例4: 搜索知识

### 代码行: 50-57

```python
print("\n=== 搜索知识 ===")
result = rag_tool.execute("search",
    query="Python编程语言的历史",
    limit=3,
    min_score=0.1
)
print(result)
```

### 完整调用链

```
┌─────────────────────────────────────────────────────────────────────────────┐
│       rag_tool.execute(action="search", query="Python编程语言的历史")       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ rag_tool.execute(action="search", query="Python编程语言的历史", limit=3)   │
│   │                                                                         │
│   └─> tools/builtin/rag_tool.py:RAGTool.execute()                         │
│       │                                                                     │
│       ├── action == "search" → return self._search(...)                    │
│       │                                                                     │
│       └─> _search(                                                         │
│               query="Python编程语言的历史",                                │
│               limit=3,                                                     │
│               min_score=0.1,                                               │
│               enable_advanced_search=True                                  │
│           )                                                                 │
│           │                                                                 │
│           ├── 验证: query 不为空                                          │
│           │                                                                 │
│           ├── 获取 pipeline:                                               │
│           │   pipeline = self._get_pipeline(namespace=None)               │
│           │   └── 返回已初始化的 "my_rag_namespace" pipeline             │
│           │                                                                 │
│           └─> pipeline["search_advanced"](..., enable_advanced_search=True)│
│               │                                                             │
│               └─> memory/rag/pipeline.py:search_advanced()                 │
│                   │                                                         │
│                   ├── store = _create_default_vector_store()                │
│                   │                                                         │
│                   ├── 生成查询扩展:                                          │
│                   │   expansions = ["Python编程语言的历史"]                  │
│                   │                                                         │
│                   │   if enable_mqe:                                        │
│                   │       └─> _prompt_mqe(query, 2)                        │
│                   │           └─> LLM 生成 2 个扩展查询                    │
│                   │               如: ["Python的历史", "Python语言发展"]     │
│                   │                                                         │
│                   │   if enable_hyde:                                       │
│                   │       └─> _prompt_hyde(query)                          │
│                   │           └─> LLM 生成假设性答案段落                  │
│                   │                                                         │
│                   │   合并去重: expansions = unique(expansions)            │
│                   │                                                         │
│                   ├── 构建过滤条件:                                          │
│                   │   where = {                                            │
│                   │       "memory_type": "rag_chunk",                       │
│                   │       "is_rag_data": True,                              │
│                   │       "data_source": "rag_pipeline",                    │
│                   │       "rag_namespace": "my_rag_namespace"               │
│                   │   }                                                    │
│                   │                                                         │
│                   ├── 对每个扩展查询进行向量检索:                             │
│                   │   agg = {}  # 用于聚合结果                               │
│                   │   per_expansion = max(1, 12 // len(expansions))         │
│                   │   for q in expansions:                                  │
│                   │       qv = embed_query(q)  # 编码查询                   │
│                   │       └─> get_text_embedder().encode(q)                │
│                   │           └── [0.2, 0.1, -0.3, ..., 0.5] (384维)      │
│                   │                                                         │
│                   │       hits = store.search_similar(                     │
│                   │           query_vector=qv,                             │
│                   │           limit=per_expansion,                          │
│                   │           score_threshold=0.1,                         │
│                   │           where=where                                   │
│                   │       )                                                 │
│                   │       │                                             │
│                   │       └─> QdrantVectorStore.search_similar()          │
│                   │           │                                         │
│                   │           └─> self.client.query_points(               │
│                   │                   collection_name="my_knowledge_collection",│
│                   │                   query=qv,                           │
│                   │                   query_filter=Filter(where),         │
│                   │                   limit=per_expansion,                │
│                   │                   score_threshold=0.1                  │
│                   │               )                                      │
│                   │               └── Qdrant HTTP API                    │
│                   │               └── 返回相似度最高的点                 │
│                   │                                                   │
│                   │       # 聚合结果: 按最高分数保留                      │
│                   │       for hit in hits:                               │
│                   │           memory_id = hit.metadata.get("memory_id")   │
│                   │           score = hit.score                           │
│                   │           if memory_id not in agg or score > agg[memory_id].score:│
│                   │               agg[memory_id] = hit                     │
│                   │                                                         │
│                   ├── 合并并排序:                                            │
│                   │   merged = list(agg.values())                           │
│                   │   merged.sort(key=lambda x: x.score, reverse=True)      │
│                   │                                                         │
│                   └── return merged[:3]  # 返回前3个结果                      │
│                                                                             │
│               ←── 返回 results: [                                            │
│                       {                                                    │
│                           "id": "a1b2c3d4_chunk_0",                        │
│                           "score": 0.85,                                   │
│                           "metadata": {                                   │
│                               "memory_id": "a1b2c3d4_chunk_0",             │
│                               "content": "Python是一种高级编程语言...",      │
│                               "source_path": ".../python_intro.md",       │
│                               "doc_id": "a1b2c3d4e5f6...",                   │
│                               "rag_namespace": "my_rag_namespace",        │
│                               ...                                           │
│                           }                                                │
│                       },                                                   │
│                       ...                                                  │
│                   ]                                                        │
│                   │                                                             │
│           ├── 格式化搜索结果:                                                  │
│           │   search_result = ["搜索结果："]                                 │
│           │   for i, result in enumerate(results, 1):                        │
│           │       meta = result["metadata"]                                  │
│           │       content = meta["content"][:200] + "..."                    │
│           │       source = meta["source_path"]                               │
│           │       score = result["score"]                                   │
│           │       search_result.append(f"\n{i}. 文档: {source} (相似度: {score:.3f})")│
│           │       search_result.append(f"   {content}")                     │
│           │                                                             │
│           └── return "\n".join(search_result)                               │
│                                                                             │
│       ←── return result_string                                               │
│                                                                             │
│←── print(result)                                                            │
│     输出:                                                                   │
│     搜索结果：                                                              │
│                                                                             │
│     1. 文档: **python_intro.md** (相似度: 0.850)                           │
│        Python是一种高级编程语言，由Guido van Rossum于1991年首次发布...      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 检索数据流

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RAG 搜索知识数据流                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  输入: query = "Python编程语言的历史", limit = 3, min_score = 0.1     │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  1. 查询扩展 (enable_advanced_search=True)                      │    │
│  │     原始查询: "Python编程语言的历史"                              │    │
│  │                                                                  │    │
│  │     MQE (多查询扩展):                                            │    │
│  │     LLM 生成 2 个扩展查询:                                        │    │
│  │     - "Python的历史"                                             │    │
│  │     - "Python语言发展"                                           │    │
│  │                                                                  │    │
│  │     HyDE (假设性文档嵌入):                                        │    │
│  │     LLM 生成假设性答案段落:                                        │    │
│  │     "Python是一种高级编程语言，由Guido van Rossum于1991年..."     │    │
│  │                                                                  │    │
│  │     最终扩展列表: [原始, MQE1, MQE2, HyDE]                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  2. 向量检索 (每个扩展查询)                                      │    │
│  │     for each expansion in expansions:                            │    │
│  │         query_embedding = encode(expansion)                      │    │
│  │         └── [0.2, 0.1, -0.3, ..., 0.5] (384维向量)               │    │
│  │                                                                  │    │
│  │         Qdrant.search_similar(                                   │    │
│  │             query_vector=query_embedding,                         │    │
│  │             filter={                                             │    │
│  │                 "memory_type": "rag_chunk",                      │    │
│  │                 "is_rag_data": true,                             │    │
│  │                 "data_source": "rag_pipeline",                   │    │
│  │                 "rag_namespace": "my_rag_namespace"              │    │
│  │             },                                                    │    │
│  │             limit=3,                                             │    │
│  │             score_threshold=0.1                                   │    │
│  │         )                                                        │    │
│  │         └── 返回相似度最高的结果                                  │    │
│  │             [                                                   │    │
│  │               {                                                 │    │
│  │                 "id": "a1b2c3d4_chunk_0",                       │    │
│  │                 "score": 0.85,                                  │    │
│  │                 "metadata": {...}                               │    │
│  │               },                                                │    │
│  │               ...                                               │    │
│  │             ]                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  3. 结果聚合                                                      │    │
│  │     agg = {}  # memory_id → hit (最高分)                         │    │
│  │     for each hit from each expansion:                            │    │
│  │         if hit.score > agg[memory_id].score:                     │    │
│  │             agg[memory_id] = hit  # 保留最高分                  │    │
│  │                                                                  │    │
│  │     merged = list(agg.values())                                   │    │
│  │     merged.sort(key=score, reverse=True)                          │    │
│  │     top_results = merged[:3]                                      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                          │
│  输出: 格式化的搜索结果                                                │
│        包含: 序号、文档名、相似度、内容预览                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 测试用例5: 获取知识库统计

### 代码行: 58-60

```python
print("\n=== 知识库统计 ===")
result = rag_tool.execute("stats")
print(result)
```

### 完整调用链

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    rag_tool.execute(action="stats")                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ rag_tool.execute(action="stats")                                          │
│   │                                                                         │
│   └─> tools/builtin/rag_tool.py:RAGTool.execute()                         │
│       │                                                                     │
│       ├── action == "stats" → return self._get_stats()                   │
│       │                                                                     │
│       └─> _get_stats(namespace=None)                                       │
│           │                                                                 │
│           ├── 获取 pipeline:                                               │
│           │   pipeline = self._get_pipeline(namespace=None)               │
│           │                                                                 │
│           └─> pipeline["get_stats"]()                                     │
│               │                                                             │
│               └─> store.get_collection_stats()                            │
│                   │                                                         │
│                   └─> QdrantVectorStore.get_collection_stats()            │
│                       │                                                     │
│                       └─> self.client.get_collection("my_knowledge_collection")│
│                           │                                                 │
│                           └── 返回集合信息:                               │
│                               {                                            │
│                                   "store_type": "qdrant",                 │
│                                   "name": "my_knowledge_collection",    │
│                                   "points_count": 3,  # 3个chunk          │
│                                   "config": {                            │
│                                       "vector_size": 384,                │
│                                       "distance": "cosine"               │
│                                   }                                       │
│                               }                                            │
│                                                                             │
│               ←── 返回 stats                                               │
│               │                                                             │
│           ├── 格式化统计信息:                                                │
│           │   stats_info = [                                               │
│           │       "📊 **RAG 知识库统计**",                                   │
│           │       "📝 命名空间: my_rag_namespace",                          │
│           │       "📋 集合名称: my_knowledge_collection",                   │
│           │       "📂 存储根路径: ./knowledge_base.json",                    │
│           │       "📦 存储类型: qdrant",                                    │
│           │       "📊 文档分块数: 3",                                        │
│           │       "🔢 向量维度: 384",                                        │
│           │       "📎 距离度量: cosine",                                    │
│           │       "",                                                     │
│           │       "🟢 **系统状态**",                                       │
│           │       "✅ RAG 管道: 正常",                                      │
│           │       "✅ LLM 连接: 正常"                                       │
│           │   ]                                                           │
│           │                                                             │
│           └── return "\n".join(stats_info)                                │
│                                                                             │
│       ←── return stats_string                                               │
│                                                                             │
│←── print(result)                                                            │
│     输出:                                                                   │
│     📊 **RAG 知识库统计**                                                  │
│     📝 命名空间: my_rag_namespace                                         │
│     📋 集合名称: my_knowledge_collection                                  │
│     📂 存储根路径: ./knowledge_base.json                                   │
│     📦 存储类型: qdrant                                                     │
│     📊 文档分块数: 3                                                        │
│     🔢 向量维度: 384                                                       │
│     📎 距离度量: cosine                                                    │
│                                                                             │
│     🟢 **系统状态**                                                        │
│     ✅ RAG 管道: 正常                                                      │
│     ✅ LLM 连接: 正常                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 完整执行时序图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        rag_demo.py 执行时序                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  时间线                                                                      │
│    │                                                                         │
│    ├─ [00:00] 初始化: LLM, Agent, RAGTool                                 │
│    │         ├─ Qdrant 连接: my_knowledge_collection                       │
│    │         ├─ 创建 RAG pipeline                                          │
│    │         └─ 输出: ✅ RAG工具初始化成功                                  │
│    │                                                                         │
│    ├─ [00:01] 测试1: 添加 "Python介绍"                                      │
│    │         ├─ 创建临时文件: python_intro.md                               │
│    │         ├─ 解析文档 → 生成 1 个 chunk                                  │
│    │         ├─ 嵌入编码 → 384维向量                                       │
│    │         ├─ Qdrant upsert                                              │
│    │         └─ 输出: ✅ 文本已添加 (分块: 1, 时间: 250ms)                  │
│    │                                                                         │
│    ├─ [00:02] 测试2: 添加 "机器学习基础"                                    │
│    │         └─ (流程同测试1)                                               │
│    │                                                                         │
│    ├─ [00:03] 测试3: 添加 "RAG概念"                                         │
│    │         └─ (流程同测试1)                                               │
│    │                                                                         │
│    ├─ [00:04] 测试4: 搜索 "Python编程语言的历史"                             │
│    │         ├─ 查询扩展 (MQE + HyDE)                                       │
│    │         ├─ 向量检索 (每个扩展查询)                                      │
│    │         ├─ 结果聚合 (保留最高分)                                        │
│    │         └─ 输出: 搜索结果 (3条，最高相似度: 0.850)                     │
│    │                                                                         │
│    └─ [00:05] 测试5: 获取统计                                               │
│              ├─ Qdrant get_collection_info                                  │
│              └─ 输出: 分块数: 3, 向量维度: 384, 距离: cosine                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## RAG 核心流程详解

### 添加知识流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         添加知识 (add_text)                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  用户输入                                                                │
│    │                                                                     │
│    └─> text: "Python是一种高级编程语言..."                             │
│        document_id: "python_intro"                                      │
│                                                                         │
│  1. 文档预处理阶段                                                        │
│    ├─> 创建临时 .md 文件                                                  │
│    ├─> MarkItDown/文本读取: 提取纯文本                                    │
│    ├─> 语言检测: langdetect → "zh"                                        │
│    ├─> 段落分割: 按标题层级                                               │
│    └─> 智能分块: chunk_size=800, overlap=100                             │
│        └── 生成 1-2 个 chunk (取决于文本长度)                             │
│                                                                         │
│  2. 向量化阶段                                                            │
│    ├─> Markdown 预处理: 移除标记符号                                      │
│    ├─> 嵌入编码: sentence-transformers                                    │
│    │   └── 输入: "Python是一种高级编程语言..."                           │
│    │   └── 输出: [0.1, -0.2, 0.3, ..., 0.4] (384维)                     │
│    └─> 批量编码 (batch_size=64)                                           │
│                                                                         │
│  3. 存储阶段                                                              │
│    ├─> 构建 Payload:                                                     │
│    │   {                                                                 │
│    │     "memory_type": "rag_chunk",                                     │
│    │     "is_rag_data": true,                                            │
│    │     "rag_namespace": "my_rag_namespace",                             │
│    │     "memory_id": chunk_id,                                          │
│    │     "content": chunk_content,                                        │
│    │     "source_path": file_path,                                       │
│    │     "doc_id": document_hash,                                        │
│    │     ...metadata                                                    │
│    │   }                                                                 │
│    │                                                                     │
│    └─> Qdrant upsert:                                                     │
│        └── PointStruct {id, vector, payload} → my_knowledge_collection    │
│                                                                         │
│  4. 清理阶段                                                              │
│    └─> 删除临时文件                                                       │
│                                                                         │
│  输出: ✅ 文本已添加 + 分块数 + 处理时间 + 命名空间                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 搜索知识流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         搜索知识 (search)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  用户输入                                                                │
│    │                                                                     │
│    └─> query: "Python编程语言的历史"                                     │
│        limit: 3, min_score: 0.1                                         │
│                                                                         │
│  1. 查询扩展阶段 (enable_advanced_search=True)                           │
│    ├─> 原始查询: "Python编程语言的历史"                                   │
│    │                                                                     │
│    ├─> MQE (多查询扩展):                                                 │
│    │   LLM 生成 2 个扩展查询                                              │
│    │   - "Python的历史"                                                  │
│    │   - "Python语言发展"                                                │
│    │                                                                     │
│    └─> HyDE (假设性文档嵌入):                                             │
│        LLM 生成假设性答案段落                                             │
│        - "Python是由Guido van Rossum创建的高级编程语言..."              │
│                                                                         │
│  2. 向量检索阶段 (每个扩展查询)                                          │
│    for expansion in [原始, MQE1, MQE2, HyDE]:                            │
│      │                                                                   │
│      ├─> 查询嵌入: encode(expansion) → 384维向量                         │
│      │                                                                   │
│      ├─> Qdrant 检索:                                                    │
│      │   search_similar(                                                 │
│      │     query_vector,                                                 │
│      │     filter={                                                      │
│      │       "memory_type": "rag_chunk",                                  │
│      │       "rag_namespace": "my_rag_namespace"                          │
│      │     },                                                            │
│      │     limit=3,                                                      │
│      │     score_threshold=0.1                                           │
│      │   )                                                              │
│      │   └── 返回按相似度排序的结果                                      │
│      │                                                                   │
│      └─> 结果聚合: 保留每个 chunk 的最高分                               │
│          agg[chunk_id] = max(hit.score)                                  │
│                                                                         │
│  3. 排序阶段                                                              │
│    ├─> merged = list(agg.values())                                        │
│    └─> merged.sort(key=score, reverse=True)                               │
│                                                                         │
│  4. 输出阶段                                                              │
│    ├─> top_results = merged[:3]                                           │
│    └─> 格式化: 序号 + 文档名 + 相似度 + 内容预览                          │
│                                                                         │
│  输出: 搜索结果列表 (最多3条)                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 关键数据结构

### RAG Chunk 数据结构 (Qdrant Payload)

```python
chunk_payload = {
    # 基础标识
    "memory_type": "rag_chunk",              # 固定值
    "memory_id": "a1b2c3d4e5f6_chunk_0",   # 唯一ID
    "is_rag_data": true,                     # RAG数据标记
    "data_source": "rag_pipeline",           # 数据来源

    # 命名空间隔离
    "rag_namespace": "my_rag_namespace",     # 命名空间

    # 内容
    "content": "Python是一种高级编程语言，由Guido van Rossum...",

    # 来源信息
    "source_path": "./knowledge_base.json/python_intro.md",
    "file_ext": ".md",
    "doc_id": "a1b2c3d4e5f6...",            # 文档哈希
    "lang": "zh",                            # 语言检测

    # 分块信息
    "start": 0,                              # 字符起始位置
    "end": 150,                              # 字符结束位置
    "heading_path": None,                    # 标题路径

    # 元数据
    "format": "markdown",
    "external": True,
    "content_hash": "xyz789..."              # 内容哈希
}
```

### RAG Pipeline 结构

```python
pipeline = {
    "store": QdrantVectorStore(...),
    "namespace": "my_rag_namespace",
    "add_documents": add_documents_func,
    "search": search_func,
    "search_advanced": search_advanced_func,
    "get_stats": get_stats_func
}
```

---

## 数据库操作总结

### Qdrant 向量数据库操作 (RAG)

| 操作 | 方法 | 数据 | Collection |
|------|------|------|------------|
| 添加知识块 | `upsert()` | PointStruct {id, vector, payload} | my_knowledge_collection |
| 搜索知识 | `query_points()` | query_vector + filter | my_knowledge_collection |
| 获取统计 | `get_collection()` | - | my_knowledge_collection |

### 过滤条件

```python
rag_filter = {
    "memory_type": "rag_chunk",      # 固定值
    "is_rag_data": True,             # 固定值
    "data_source": "rag_pipeline",   # 固定值
    "rag_namespace": "my_rag_namespace"  # 可变，用于多租户隔离
}
```

---

## RAG vs Memory 对比

| 特性 | RAG Tool | Memory Tool |
|------|----------|-------------|
| 用途 | 知识库检索增强 | 对话记忆管理 |
| 数据类型 | 文档分块 (chunk) | 记忆项 (memory) |
| memory_type | rag_chunk | working, episodic, semantic, perceptual |
| 命名空间 | rag_namespace (多租户) | user_id (用户隔离) |
| 分块策略 | 固定 chunk_size=800, overlap=100 | 不分块 (完整内容) |
| 检索增强 | MQE (多查询) + HyDE | 图检索 (Neo4j) |
| 存储集合 | 独立 collection | 共享 collection |
| 主要操作 | add_document, add_text, ask, search | add, search, summary, stats |

---

## 总结

`demo/rag_demo.py` 演示了完整的 RAG 知识库功能：

### 核心特点

1. **多格式文档支持** - 通过 MarkItDown 支持 PDF、Office、图片、音频等多种格式
2. **智能分块** - 按段落和标题层级分块，带重叠保持上下文
3. **查询扩展** - MQE (多查询扩展) + HyDE (假设性文档嵌入)
4. **命名空间隔离** - 通过 rag_namespace 支持多项目/多租户
5. **向量检索** - 基于 Qdrant 的高效相似度搜索

### 数据流程

```
文档 → MarkItDown解析 → Markdown文本 → 智能分块 →
向量化 → Qdrant存储 → (添加完成)

查询 → 扩展(MQE+HyDE) → 多路向量检索 → 结果聚合 →
排序输出 → (搜索完成)
```

### 适用场景

- **知识库问答** - 企业文档、技术文档、FAQ等
- **智能客服** - 产品手册、使用指南
- **学习辅助** - 课程材料、学习笔记
- **研究助手** - 论文、报告、文献资料
