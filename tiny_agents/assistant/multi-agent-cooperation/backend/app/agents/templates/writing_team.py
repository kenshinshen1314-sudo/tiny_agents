from app.models.team import TeamTemplate

WRITING_TEAM_TEMPLATE = TeamTemplate(
    id="writing_team",
    name="内容创作团队",
    description="适用于内容创作",
    task_type="writing",
    roles=[
        "ChiefEditor",
        "Writer",
        "Editor",
        "Reviewer"
    ],
    execution_flow=[
        {"step": 1, "role": "ChiefEditor", "parallel": False},
        {"step": 2, "role": "Writer", "parallel": False},
        {"step": 3, "role": "Editor", "parallel": False},
        {"step": 4, "role": "Reviewer", "parallel": False}
    ]
)