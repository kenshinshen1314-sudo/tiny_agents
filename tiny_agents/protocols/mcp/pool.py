"""
MCP 客户端连接池

复用 MCP 客户端连接，避免每次工具调用都重新启动服务器
"""
import asyncio
from typing import Optional, Dict, Any, List
import json


class MCPClientPool:
    """MCP 客户端连接池 - 单例模式"""
    
    _instance: Optional['MCPClientPool'] = None
    _lock = asyncio.Lock()
    
    def __init__(self):
        self._pools: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
    
    @classmethod
    def get_instance(cls) -> 'MCPClientPool':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def get_client(self, server_command, server_args, env):
        """获取或创建 MCP 客户端"""
        # 创建唯一键（排除敏感信息）
        key = self._make_key(server_command, server_args)
        
        async with self._lock:
            if key not in self._pools:
                # 延迟导入避免循环依赖
                from .client import MCPClient
                client = MCPClient(server_command, server_args, env=env)
                await client.__aenter__()
                self._pools[key] = client
            
            return self._pools[key]
    
    def _make_key(self, server_command, server_args):
        """创建连接的唯一键"""
        return json.dumps({
            "command": str(server_command),
            "args": str(server_args),
        }, sort_keys=True)
    
    async def cleanup(self):
        """清理所有连接"""
        async with self._lock:
            for client in self._pools.values():
                try:
                    await client.__aexit__(None, None, None)
                except Exception:
                    pass
            self._pools.clear()


# 全局单例
_global_pool: Optional[MCPClientPool] = None


def get_mcp_pool() -> MCPClientPool:
    """获取全局 MCP 连接池"""
    global _global_pool
    if _global_pool is None:
        _global_pool = MCPClientPool.get_instance()
    return _global_pool
