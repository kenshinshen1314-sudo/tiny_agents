from typing import Dict, Any, Optional
from app.models.team import TeamTemplate

class AgentPool:
    def __init__(self, max_size: int = 5):
        self.max_size = max_size
        self.pools: Dict[str, list] = {}

    def get(self, role_name: str):
        if role_name not in self.pools:
            self.pools[role_name] = []
        pool = self.pools[role_name]
        if pool:
            return pool.pop()
        return None

    def release(self, role_name: str, agent):
        if role_name not in self.pools:
            self.pools[role_name] = []
        pool = self.pools[role_name]
        if len(pool) < self.max_size:
            pool.append(agent)

class SimpleAgent:
    def __init__(self, role_name: str, role_prompt: str):
        self.role_name = role_name
        self.role_prompt = role_prompt

    async def run(self, task: str) -> str:
        return f"[{self.role_name}] 已完成: {task}"

class AgentFactory:
    def __init__(self):
        from app.agents.templates.dev_team import DEV_TEAM_TEMPLATE
        from app.agents.templates.writing_team import WRITING_TEAM_TEMPLATE

        self.templates: Dict[str, TeamTemplate] = {
            "dev_team": DEV_TEAM_TEMPLATE,
            "dev_team_lite": DEV_TEAM_TEMPLATE,
            "writing_team": WRITING_TEAM_TEMPLATE
        }
        self.role_prompts = self._load_role_prompts()
        self.agent_pool = AgentPool()

    def _load_role_prompts(self) -> Dict[str, str]:
        return {
            "ProductManager": "你是一名资深产品经理，擅长需求分析和PRD撰写。",
            "Architect": "你是一名系统架构师，擅长技术方案设计。",
            "FrontendDev": "你是一名前端开发工程师，擅长Vue/React开发。",
            "BackendDev": "你是一名后端开发工程师，擅长Python/Go开发。",
            "QAEngineer": "你是一名QA工程师，擅长测试用例编写。",
            "ChiefEditor": "你是一名主编，擅长内容策划和整体把控。",
            "Writer": "你是一名专业作家，擅长各类文章撰写。",
            "Editor": "你是一名文字编辑，擅长润色和优化。",
            "Reviewer": "你是一名审稿专家，擅长内容审核和质量评估。"
        }

    def get_template(self, template_id: str) -> Optional[TeamTemplate]:
        return self.templates.get(template_id)

    def list_templates(self):
        return list(self.templates.values())

    def create_agent(self, role_name: str):
        agent = self.agent_pool.get(role_name)
        if agent:
            return agent

        role_prompt = self.role_prompts.get(role_name, f"你是一个{role_name}。")
        return SimpleAgent(role_name, role_prompt)

    def release_agent(self, role_name: str, agent):
        self.agent_pool.release(role_name, agent)