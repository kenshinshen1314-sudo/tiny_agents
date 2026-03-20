from typing import Dict, Any, List, Optional
from app.models.task import Task, TaskStatus, TaskType, TaskComplexity
from app.models.team import Team, TeamTemplate, Role
from app.agents.team_leader import TeamLeader
from app.agents.agent_factory import AgentFactory
import uuid

class TaskAnalyzer:
    """任务分析器"""

    def analyze(self, user_input: str) -> Dict[str, Any]:
        input_lower = user_input.lower()
        dev_keywords = ["开发", "代码", "系统", "网站", "app", "前端", "后端", "软件", "接口"]
        writing_keywords = ["文章", "写作", "内容", "文档", "报告", "文案", "创作", "写一篇"]

        complexity = TaskComplexity.NORMAL
        if len(user_input) < 20:
            complexity = TaskComplexity.SIMPLE
        elif len(user_input) > 200:
            complexity = TaskComplexity.COMPLEX

        is_dev = any(k in input_lower for k in dev_keywords)
        task_type = TaskType.DEV if is_dev else TaskType.WRITING

        return {
            "task_type": task_type,
            "complexity": complexity,
            "keywords": []
        }

class TeamManager:
    """TeamManager - 顶层协调者"""

    def __init__(self):
        self.analyzer = TaskAnalyzer()
        self.agent_factory = AgentFactory()
        self.active_teams: Dict[str, Team] = {}

    def analyze_task(self, user_input: str) -> Dict[str, Any]:
        return self.analyzer.analyze(user_input)

    def build_team(self, template_id: str, task_id: str) -> Team:
        template = self.agent_factory.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        roles = []
        for role_name in template.roles:
            role = Role(name=role_name, status="idle", dependencies=[])
            roles.append(role)

        team = Team(
            task_id=task_id,
            template_id=template_id,
            roles=roles,
            status="ready"
        )

        self.active_teams[task_id] = team
        return team

    async def coordinate(self, task_id: str) -> Dict[str, Any]:
        team = self.active_teams.get(task_id)
        if not team:
            return {"error": "Team not found"}

        template = self.agent_factory.get_template(team.template_id)
        team_leader = TeamLeader(
            team=team,
            template=template,
            agent_factory=self.agent_factory
        )

        result = await team_leader.execute()
        return result

    def get_team_status(self, task_id: str) -> Optional[Team]:
        return self.active_teams.get(task_id)

team_manager = TeamManager()