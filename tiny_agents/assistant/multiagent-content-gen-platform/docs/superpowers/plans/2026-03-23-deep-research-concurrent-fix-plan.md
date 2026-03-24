# 深度研究任务并发失败修复实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复深度研究任务在并发执行时偶尔失败的问题（搜索返回空结果）

**Architecture:** 通过添加任务级重试机制、指数退避策略和线程本地 SearchTool 实例，解决并发竞争和 API 限流问题

**Tech Stack:** Python, threading, tiny_agents

---

## 实现概览

需要修改的文件：
- `src/services/search.py` - 添加异常类、线程本地 SearchTool、重试逻辑
- `src/agent.py` - 在任务执行中集成重试机制
- `src/config.py` - 添加重试配置项（可选）

---

## Chunk 1: 搜索服务修改

### Task 1: 添加可重试异常类

**Files:**
- Modify: `src/services/search.py:1-20`

- [ ] **Step 1: 在 search.py 开头添加异常类**

在文件顶部的 import 部分之后添加：

```python
class RetryableSearchError(Exception):
    """可重试的搜索错误（限流、超时、网络错误等）"""
    pass


class NonRetryableSearchError(Exception):
    """不可重试的搜索错误（API 密钥错误等）"""
    pass
```

- [ ] **Step 2: 添加 threading import**

在文件顶部添加：
```python
import threading
```

- [ ] **Step 3: 添加线程本地存储**

在 `MAX_TOKENS_PER_SOURCE` 之后添加：
```python
_thread_local = threading.local()


def get_search_tool(backend: str) -> "SearchTool":
    """获取当前线程的 SearchTool 实例"""
    if not hasattr(_thread_local, 'search_tool') or _thread_local.search_tool is None:
        _thread_local.search_tool = SearchTool(backend=backend)
    return _thread_local.search_tool
```

- [ ] **Step 4: 提交更改**

```bash
git add src/services/search.py
git commit -m "feat(search): add retryable exceptions and thread-local SearchTool"
```

---

### Task 2: 修改 dispatch_search 使用线程本地 SearchTool

**Files:**
- Modify: `src/services/search.py:23-78`

- [ ] **Step 1: 修改 dispatch_search 函数使用 get_search_tool**

找到 `dispatch_search` 函数，将第33行的全局 SearchTool 调用改为：

```python
def dispatch_search(
    query: str,
    config: Configuration,
    loop_count: int,
) -> Tuple[dict[str, Any] | None, list[str], Optional[str], str]:
    """Execute configured search backend and normalise response payload."""

    search_api = get_config_value(config.search_api)

    try:
        search_tool = get_search_tool(search_api)
        raw_response = search_tool.run(
            {
                "input": query,
                "backend": search_api,
                "mode": "structured",
                "fetch_full_page": config.fetch_full_page,
                "max_results": 5,
                "max_tokens_per_source": MAX_TOKENS_PER_SOURCE,
                "loop_count": loop_count,
            }
        )
    except Exception as exc:
        # 检查是否是可重试的错误
        error_msg = str(exc).lower()
        if any(keyword in error_msg for keyword in ['timeout', 'rate limit', '429', 'connection', 'network']):
            raise RetryableSearchError(f"Search failed (retryable): {exc}")
        elif any(keyword in error_msg for keyword in ['api key', 'unauthorized', 'forbidden', 'invalid']):
            raise NonRetryableSearchError(f"Search failed (non-retryable): {exc}")
        else:
            raise
```

- [ ] **Step 2: 确保 dispatch_search 返回正确的格式**

原函数的返回值结构保持不变，异常处理添加后不影响正常返回。

- [ ] **Step 3: 提交更改**

```bash
git add src/services/search.py
git commit -m "feat(search): use thread-local SearchTool instance"
```

---

## Chunk 2: Agent 任务执行重试

### Task 3: 在 agent.py 中添加重试逻辑

**Files:**
- Modify: `src/agent.py:307-431`

- [ ] **Step 1: 添加重试配置和 import**

在文件顶部添加：
```python
import time
```

在 agent 类的 `__init__` 方法后添加配置属性：

```python
# 重试配置
self.max_task_retries = 3
self.retry_delays = [1, 2, 4]  # 指数退避（秒）
```

- [ ] **Step 2: 修改 _execute_task 方法添加重试逻辑**

将 `_execute_task` 方法修改为包含重试逻辑。保留原有逻辑，包装在 try-except 中：

```python
def _execute_task(
    self,
    state: SummaryState,
    task: TodoItem,
    *,
    emit_stream: bool,
    step: int | None = None,
) -> Iterator[dict[str, Any]]:
    """Run search + summarization for a single task with retry."""

    from services.search import RetryableSearchError

    for attempt in range(self.max_task_retries):
        try:
            # 调用实际的执行逻辑
            return self._execute_task_impl(state, task, emit_stream=emit_stream, step=step)
        except RetryableSearchError as e:
            if attempt == self.max_task_retries - 1:
                # 所有重试都失败，记录失败状态
                logger.error(f"Task {task.id} failed after {self.max_task_retries} attempts: {e}")
                task.status = "failed"
                if emit_stream:
                    yield {
                        "type": "task_status",
                        "task_id": task.id,
                        "status": "failed",
                        "detail": str(e),
                        "title": task.title,
                        "intent": task.intent,
                    }
                return

            wait_time = self.retry_delays[attempt]
            logger.warning(
                f"Task {task.id} retry {attempt + 1}/{self.max_task_retries}, "
                f"waiting {wait_time}s: {e}"
            )
            if emit_stream:
                yield {
                    "type": "status",
                    "message": f"任务 {task.id} 重试中 ({attempt + 1}/{self.max_task_retries})...",
                    "task_id": task.id,
                }
            time.sleep(wait_time)


def _execute_task_impl(
    self,
    state: SummaryState,
    task: TodoItem,
    *,
    emit_stream: bool,
    step: int | None = None,
) -> Iterator[dict[str, Any]]:
    """实际的任务执行逻辑（不含重试）"""
    # 原 _execute_task 的逻辑保持不变
    task.status = "in_progress"

    # ... (原有逻辑完全保留)
```

- [ ] **Step 3: 提交更改**

```bash
git add src/agent.py
git commit -m "feat(agent): add retry logic with exponential backoff"
```

---

## Chunk 3: 配置项（可选）

### Task 4: 添加重试配置到 config.py（可选）

**Files:**
- Modify: `src/config.py`

- [ ] **Step 1: 添加重试配置项**

在 Configuration 类中添加可选的重试配置：

```python
class Configuration:
    # ... 现有配置 ...

    # 重试配置
    max_task_retries: int = 3
    retry_delays: List[int] = field(default_factory=lambda: [1, 2, 4])
```

- [ ] **Step 2: 提交更改（可选）**

如果用户需要可配置的重试参数，可以提交此更改。

---

## 验收测试

### 手动测试

1. 启动后端服务
2. 调用流式 API 执行深度研究（3-5个任务）
3. 观察日志中是否有重试信息
4. 确认所有任务都成功完成，没有被标记为 skipped 或 failed

### 日志验证

预期日志输出：
- `"Task N retry 1/3, waiting 1s: ..."` - 重试开始
- `"Task N retry 2/3, waiting 2s: ..."` - 第二次重试
- `"Task N succeeded on attempt N"` - 重试成功

---

## 计划完成

**Plan complete and saved to `docs/superpowers/plans/2026-03-23-deep-research-concurrent-fix-plan.md`. Ready to execute?**