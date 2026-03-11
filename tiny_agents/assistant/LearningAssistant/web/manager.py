"""
助手实例管理器
管理多个用户独立的 PDFParserAssistant 实例
"""

import asyncio
from typing import Dict, Optional
import logging

from ..PDFParserAssistant import PDFParserAssistant

logger = logging.getLogger(__name__)


class AssistantManager:
    """管理多个用户独立的 PDFParserAssistant 实例"""

    def __init__(self):
        self._assistants: Dict[str, PDFParserAssistant] = {}
        self._lock = asyncio.Lock()

    async def get_or_create(self, user_id: str) -> PDFParserAssistant:
        """
        获取或创建指定用户的助手实例

        Args:
            user_id: 用户ID

        Returns:
            PDFParserAssistant: 助手实例
        """
        async with self._lock:
            if user_id not in self._assistants:
                logger.info(f"Creating new assistant instance for user: {user_id}")
                self._assistants[user_id] = PDFParserAssistant(user_id=user_id)
            return self._assistants[user_id]

    async def get(self, user_id: str) -> Optional[PDFParserAssistant]:
        """
        获取指定用户的助手实例（不存在则返回None）

        Args:
            user_id: 用户ID

        Returns:
            Optional[PDFParserAssistant]: 助手实例或None
        """
        async with self._lock:
            return self._assistants.get(user_id)

    async def remove(self, user_id: str) -> bool:
        """
        移除指定用户的助手实例

        Args:
            user_id: 用户ID

        Returns:
            bool: 是否成功移除
        """
        async with self._lock:
            if user_id in self._assistants:
                del self._assistants[user_id]
                logger.info(f"Removed assistant instance for user: {user_id}")
                return True
            return False

    async def list_users(self) -> list[str]:
        """
        列出所有有助手实例的用户

        Returns:
            list[str]: 用户ID列表
        """
        async with self._lock:
            return list(self._assistants.keys())


# 全局单例
_manager: Optional[AssistantManager] = None


def get_manager() -> AssistantManager:
    """获取全局助手管理器实例"""
    global _manager
    if _manager is None:
        _manager = AssistantManager()
    return _manager
