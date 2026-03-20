from app.models.team import TeamTemplate
from typing import List, Dict, Any

class TemplateService:
    def __init__(self):
        self.templates = self._load_default_templates()

    def _load_default_templates(self) -> List[TeamTemplate]:
        return [
            TeamTemplate(
                id="dev_team",
                name="软件开发团队",
                description="适用于软件开发项目，包含PM、架构师、前后端开发、测试等角色",
                task_type="dev",
                roles=["ProductManager", "Architect", "FrontendDev", "BackendDev", "QAEngineer"],
                execution_flow=[
                    {"step": 1, "role": "ProductManager", "parallel": False},
                    {"step": 2, "role": "Architect", "parallel": False},
                    {"step": 3, "roles": ["FrontendDev", "BackendDev"], "parallel": True},
                    {"step": 4, "role": "QAEngineer", "parallel": False}
                ]
            ),
            TeamTemplate(
                id="dev_team_lite",
                name="软件开发团队（精简版）",
                description="适用于简单项目，仅包含核心角色",
                task_type="dev",
                roles=["ProductManager", "BackendDev", "QAEngineer"],
                execution_flow=[
                    {"step": 1, "role": "ProductManager"},
                    {"step": 2, "role": "BackendDev"},
                    {"step": 3, "role": "QAEngineer"}
                ]
            ),
            TeamTemplate(
                id="writing_team",
                name="内容创作团队",
                description="适用于内容创作，包含主编、作家、编辑、审稿等角色",
                task_type="writing",
                roles=["ChiefEditor", "Writer", "Editor", "Reviewer"],
                execution_flow=[
                    {"step": 1, "role": "ChiefEditor"},
                    {"step": 2, "role": "Writer"},
                    {"step": 3, "role": "Editor"},
                    {"step": 4, "role": "Reviewer"}
                ]
            )
        ]

    def list_templates(self) -> List[TeamTemplate]:
        return self.templates

    def get_template(self, template_id: str) -> TeamTemplate:
        for t in self.templates:
            if t.id == template_id:
                return t
        return None

    async def analyze_and_recommend(self, user_input: str) -> Dict[str, Any]:
        user_input_lower = user_input.lower()
        dev_keywords = ["开发", "代码", "系统", "网站", "app", "前端", "后端", "软件"]
        writing_keywords = ["文章", "写作", "内容", "文档", "报告", "文案", "创作"]

        is_dev = any(k in user_input_lower for k in dev_keywords)
        is_writing = any(k in user_input_lower for k in writing_keywords)

        recommended = "dev_team" if is_dev else "writing_team" if is_writing else "dev_team"

        return {
            "task_type": "dev" if is_dev else "writing",
            "complexity": "normal",
            "recommended_template": recommended,
            "available_templates": [t.id for t in self.templates]
        }