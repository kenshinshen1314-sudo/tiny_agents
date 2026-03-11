"""Tiny Agents - 轻量级 AI Agent 框架"""

from .core.llm import HelloAgentsLLM

# 可选的旧模块导入（可能缺失依赖）
try:
    from .agents.react_agent_old import ReActAgent
    _has_react_old = True
except ImportError:
    _has_react_old = False

try:
    from .tools.builtin.search import ToolExecutor, search
    _has_search = True
except ImportError:
    _has_search = False

__all__ = [
    "HelloAgentsLLM",
]

if _has_react_old:
    __all__.append("ReActAgent")

if _has_search:
    __all__.extend(["ToolExecutor", "search"])