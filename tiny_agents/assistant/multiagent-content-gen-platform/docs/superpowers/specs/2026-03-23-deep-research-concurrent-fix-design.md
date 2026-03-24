# 深度研究任务并发失败修复设计

**日期**：2026-03-23
**状态**：已确认

## 1. 问题现状

- **触发方式**：流式 API (`run_stream`) 使用多线程并行执行任务
- **失败频率**：偶尔失败（1-2个任务）
- **失败表现**：搜索返回空结果，任务被标记为 `skipped`
- **根本原因**：
  1. 全局共享 SearchTool 单例 (`search.py:20`) 被多线程同时调用
  2. DuckDuckGo DDGS 使用上下文管理器，非线程安全
  3. 多个并发请求触发 API 限流 (rate limit)

## 2. 解决方案：任务级重试 + 指数退避

### 2.1 核心修改点

#### 2.1.1 可重试异常类

创建两类搜索异常，区分可重试和不可重试的错误：

```python
# search.py
class RetryableSearchError(Exception):
    """可重试的搜索错误（限流、超时等）"""
    pass

class NonRetryableSearchError(Exception):
    """不可重试的搜索错误（API 密钥错误等）"""
    pass
```

#### 2.1.2 线程本地 SearchTool

使用 `threading.local()` 为每个线程创建独立的 SearchTool 实例：

```python
# search.py
_thread_local = threading.local()

def get_search_tool(backend: str) -> SearchTool:
    if not hasattr(_thread_local, 'search_tool') or _thread_local.search_tool is None:
        _thread_local.search_tool = SearchTool(backend=backend)
    return _thread_local.search_tool
```

#### 2.1.3 重试装饰器

创建可重试的搜索调用封装：

```python
def search_with_retry(query: str, config: Configuration, max_retries: int = 3):
    """带重试的搜索调用"""
    for attempt in range(max_retries):
        try:
            return dispatch_search(query, config)
        except RetryableSearchError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # 指数退避: 1s, 2s, 4s
            logger.warning(f"Search retry {attempt+1}/{max_retries}, waiting {wait_time}s: {e}")
            time.sleep(wait_time)
```

#### 2.1.4 任务执行器重试逻辑

在 `agent.py` 的 `_execute_task` 中添加重试：

```python
def _execute_task(self, state, task, *, emit_stream, step=None):
    max_retries = 3
    retry_delays = [1, 2, 4]  # 指数退避（秒）

    for attempt in range(max_retries):
        try:
            return self._execute_task_impl(state, task, emit_stream, step)
        except RetryableSearchError as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Task {task.id} retry {attempt+1}/{max_retries}, waiting {retry_delays[attempt]}s")
            time.sleep(retry_delays[attempt])
```

### 2.2 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `src/services/search.py` | 添加异常类、线程本地 SearchTool、重试逻辑 |
| `src/agent.py` | 在 `_execute_task` 中集成重试机制 |
| `src/config.py` | 可选：添加重试配置项 |

### 2.3 重试策略

| 错误类型 | 处理方式 | 重试 |
|---------|---------|------|
| API 限流 (429) | 指数退避后重试 | ✅ |
| 超时 | 等待后重试 | ✅ |
| 网络错误 | 等待后重试 | ✅ |
| 无搜索结果 | **不重试**（查询问题） | ❌ |
| API 密钥错误 | 立即失败 | ❌ |

### 2.4 日志监控

- 重试开始：`"Task {id} starting attempt {n}/{max}"`
- 重试成功：`"Task {id} succeeded on attempt {n}"`
- 重试失败：`"Task {id} failed after {n} attempts: {error}"`

## 3. 数据流

```
run_stream()
    │
    ├──▶ 创建任务线程 (Thread 1, 2, 3, ...)
    │       │
    │       ├──▶ _execute_task() [with retry]
    │       │       │
    │       │       ├── 尝试1: dispatch_search()
    │       │       │           │
    │       │       │           ├── RetryableError? ──▶ 重试
    │       │       │           └── 成功 ──▶ 继续
    │       │       │
    │       │       └── 成功 ──▶ summarizer.summarize_task()
    │       │
    │       └──▶ 事件入队 (enqueue)
    │
    └──▶ 主循环收集事件并 yield
```

## 4. 验收标准

1. ✅ 多个任务并发执行时，不再出现因竞争导致的空搜索结果
2. ✅ API 限流时自动重试，不阻塞任务执行
3. ✅ 重试失败的任务正确标记为 `failed`，并记录错误信息
4. ✅ 日志清晰记录重试过程，便于调试