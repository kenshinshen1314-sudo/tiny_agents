"""Content generation service for自媒体内容创作."""

from __future__ import annotations

import logging
from typing import Any, Iterator, Optional

from tiny_agents.agents import ToolAwareSimpleAgent
from tiny_agents.core.llm import HelloAgentsLLM

from config import Configuration
import sys
from pathlib import Path
# Add backend/src to path for prompts module
_services_dir = Path(__file__).parent.parent
if str(_services_dir) not in sys.path:
    sys.path.insert(0, str(_services_dir))
from prompts import content_creation_user_template, load_article_style_prompt

logger = logging.getLogger(__name__)

# Style mapping for content generation
STYLE_MAP = {
    "rational": "理性深度",
    "emotional": "情感共鸣",
    "humor": "轻松幽默",
    "sharp": "犀利观点",
}

# Platform mapping
PLATFORM_MAP = {
    "wechat": "微信公众号",
    "xhs": "小红书",
    "douyin": "抖音",
}


class ContentGenerationService:
    """Service for generating 自媒体 content from user materials."""

    def __init__(
        self,
        content_agent: ToolAwareSimpleAgent,
        config: Configuration,
    ) -> None:
        """Initialize the content generation service."""
        self._agent = content_agent
        self._config = config

    def generate_content(
        self,
        topic: str,
        platform: str = "wechat",
        style: str = "rational",
    ) -> Iterator[str]:
        """Generate content in streaming mode.

        Args:
            topic: User's material/topic input
            platform: Target platform (wechat/xhs/douyin)
            style: Desired style (rational/emotional/humor/sharp)

        Yields:
            Content chunks as they are generated
        """
        user_prompt = content_creation_user_template.format(
            topic=topic,
            platform=platform,
            platform_desc=PLATFORM_MAP.get(platform, platform),
            style=style,
            style_desc=STYLE_MAP.get(style, style),
        )

        logger.info(
            f"Generating content for topic={topic}, platform={platform}, style={style}"
        )

        try:
            # Stream the response
            response = self._agent.run(user_prompt)

            if hasattr(response, "__iter__"):
                for chunk in response:
                    if chunk:
                        yield chunk
            else:
                # Non-streaming response
                yield str(response)

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise

    def generate_content_sync(
        self,
        topic: str,
        platform: str = "wechat",
        style: str = "rational",
    ) -> dict[str, Any]:
        """Generate content in synchronous mode.

        Args:
            topic: User's material/topic input
            platform: Target platform (wechat/xhs/douyin)
            style: Desired style (rational/emotional/humor/sharp)

        Returns:
            Dictionary containing generated content and metadata
        """
        user_prompt = content_creation_user_template.format(
            topic=topic,
            platform=platform,
            platform_desc=PLATFORM_MAP.get(platform, platform),
            style=style,
            style_desc=STYLE_MAP.get(style, style),
        )

        logger.info(
            f"Generating content sync for topic={topic}, platform={platform}, style={style}"
        )

        try:
            response = self._agent.run(user_prompt)
            content = str(response) if response else ""

            return {
                "content": content,
                "platform": platform,
                "style": style,
                "topic": topic,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Content generation sync failed: {e}")
            return {
                "content": "",
                "platform": platform,
                "style": style,
                "topic": topic,
                "success": False,
                "error": str(e),
            }