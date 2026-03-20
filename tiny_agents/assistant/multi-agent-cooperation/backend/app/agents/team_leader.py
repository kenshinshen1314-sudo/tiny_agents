from typing import Dict, Any, List
from app.models.team import Team, TeamTemplate, Role
from app.agents.agent_factory import AgentFactory

class TeamLeader:
    """TeamLeader - 领域协调者"""

    def __init__(self, team: Team, template: TeamTemplate, agent_factory: AgentFactory):
        self.team = team
        self.template = template
        self.agent_factory = agent_factory

    async def execute(self) -> Dict[str, Any]:
        results = {}

        for flow_step in self.template.execution_flow:
            step = flow_step["step"]

            if flow_step.get("parallel", False):
                roles_to_execute = flow_step.get("roles", [])
                step_results = await self._execute_parallel(roles_to_execute)
            else:
                role_name = flow_step.get("role")
                if role_name:
                    step_results = await self._execute_role(role_name)

            results[f"step_{step}"] = step_results

        return {
            "status": "completed",
            "results": results
        }

    async def _execute_role(self, role_name: str) -> Dict[str, Any]:
        role = None
        for r in self.team.roles:
            if r.name == role_name:
                role = r
                break

        if not role:
            return {"error": f"Role {role_name} not found"}

        from app.models.team import RoleStatus
        role.status = RoleStatus.WORKING

        try:
            agent = self.agent_factory.create_agent(role_name)
            result = await agent.run(f"执行{role_name}任务")

            role.status = RoleStatus.COMPLETED
            role.output = result

            return {
                "role": role_name,
                "status": "completed",
                "output": result
            }
        except Exception as e:
            role.status = RoleStatus.FAILED
            return {
                "role": role_name,
                "status": "failed",
                "error": str(e)
            }

    async def _execute_parallel(self, role_names: List[str]) -> Dict[str, Any]:
        import asyncio
        tasks = [self._execute_role(name) for name in role_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "roles": role_names,
            "results": results
        }