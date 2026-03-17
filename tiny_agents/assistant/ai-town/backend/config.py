"""配置文件"""

import os
from pathlib import Path
from typing import Optional

# 加载 .env 文件
from dotenv import load_dotenv

# 获取当前文件目录，并加载同目录下的 .env 文件
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

class Settings:
    """应用配置"""

    # API配置
    API_TITLE = "赛博小镇 API"
    API_VERSION = "1.0.0"
    API_HOST: str = os.getenv("HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("PORT", "8000"))

    # NPC配置
    NPC_UPDATE_INTERVAL = 30  # NPC状态更新间隔(秒)

    # LLM配置 (从环境变量读取)
    LLM_MODEL_ID: str = os.getenv("LLM_MODEL_ID", "Qwen/Qwen2.5-72B-Instruct")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "custom")
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api-inference.modelscope.cn/v1/")
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # CORS配置
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    # Unsplash API
    UNSPLASH_ACCESS_KEY: Optional[str] = os.getenv("UNSPLASH_ACCESS_KEY")
    UNSPLASH_SECRET_KEY: Optional[str] = os.getenv("UNSPLASH_SECRET_KEY")

    # 高德地图API
    AMAP_API_KEY: Optional[str] = os.getenv("AMAP_API_KEY")

    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.LLM_API_KEY:
            print("⚠️  警告: 未设置LLM_API_KEY环境变量")
            print("   请在.env文件中配置LLM_API_KEY")
            print("   示例: LLM_API_KEY=\"your-api-key\"")
            return False

        print(f"✅ LLM配置:")
        print(f"   模型: {cls.LLM_MODEL_ID}")
        print(f"   服务地址: {cls.LLM_BASE_URL}")
        return True

settings = Settings()
