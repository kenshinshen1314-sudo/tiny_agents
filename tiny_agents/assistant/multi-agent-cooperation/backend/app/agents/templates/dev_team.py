from app.models.team import TeamTemplate

DEV_TEAM_TEMPLATE = TeamTemplate(
    id="dev_team",
    name="软件开发团队",
    description="适用于软件开发项目",
    task_type="dev",
    roles=[
        "ProductManager",
        "Architect",
        "FrontendDev",
        "BackendDev",
        "QAEngineer"
    ],
    execution_flow=[
        {"step": 1, "role": "ProductManager", "parallel": False},
        {"step": 2, "role": "Architect", "parallel": False},
        {"step": 3, "roles": ["FrontendDev", "BackendDev"], "parallel": True},
        {"step": 4, "role": "QAEngineer", "parallel": False}
    ]
)