from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Multi-Agent Cooperation"
    debug: bool = True
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-20250514"
    max_concurrent_tasks: int = 10
    max_agents_per_task: int = 5
    agent_pool_max_size: int = 5
    agent_pool_timeout: int = 1800
    data_dir: str = "./data"
    tasks_dir: str = "./data/tasks"

    class Config:
        env_file = ".env"

settings = Settings()