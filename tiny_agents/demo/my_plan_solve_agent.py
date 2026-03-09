# 自定义 PlanAndSolve Agent 提示词模板

# 规划器提示词 - 更详细的规划指导
MY_PLANNER_PROMPT = """
你是一位经验丰富的任务规划专家。你的核心能力是将复杂的用户需求拆解为清晰、可执行的步骤序列。

## 规划原则
1. **步骤独立性**：每个步骤应该是可以独立完成的任务
2. **逻辑递进**：步骤之间应该有清晰的逻辑依赖关系
3. **粒度适中**：步骤不应过于细化，也不应过于笼统
4. **可验证性**：每个步骤的完成应该是可验证的

## 任务要求
请分析以下用户问题，生成一个结构化的执行计划。

用户问题: {question}

## 输出格式
请严格按照以下格式输出你的计划:
```python
["步骤1: 具体描述", "步骤2: 具体描述", "步骤3: 具体描述", ...]
```

开始规划:
"""

# 执行器提示词 - 强调精确执行
MY_EXECUTOR_PROMPT = """
你是一位精确的任务执行专家。你的职责是严格按照既定计划，一步步完成每个步骤的任务。

## 执行原则
1. **专注当前**：只关注当前步骤，不要跳步或预判后续步骤
2. **简洁明了**：直接给出当前步骤的答案，避免冗余解释
3. **保持连贯**：参考历史步骤的结果，保持推理的连贯性
4. **准确输出**：确保输出的内容是对当前步骤的直接回应

## 任务上下文
# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

## 输出要求
请仅输出针对"当前步骤"的回答:
"""

import re
from typing import Optional, List, Dict
from tiny_agents.agents import PlanAndSolveAgent
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.core.config import Config
from tiny_agents.core.message import Message


class MyPlanAndSolveAgent(PlanAndSolveAgent):
    """
    自定义的 Plan and Solve Agent - 分解规划与逐步执行的智能体

    特点：
    1. 使用自定义的规划器和执行器提示词模板
    2. 支持更详细的规划指导和执行要求
    3. 可以进一步扩展以支持工具调用、多轮交互等功能
    """

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        custom_prompts: Optional[Dict[str, str]] = None,
        enable_detailed_logging: bool = False
    ):
        """
        初始化 MyPlanAndSolveAgent

        Args:
            name: Agent名称
            llm: LLM实例
            system_prompt: 系统提示词
            config: 配置对象
            custom_prompts: 自定义提示词模板 {"planner": "", "executor": ""}
            enable_detailed_logging: 是否启用详细日志
        """
        # 准备自定义提示词（如果用户没有提供，使用默认的）
        if custom_prompts is None:
            custom_prompts = {
                "planner": MY_PLANNER_PROMPT,
                "executor": MY_EXECUTOR_PROMPT
            }

        # 调用父类初始化
        super().__init__(name, llm, system_prompt, config, custom_prompts)

        # 额外的配置
        self.enable_detailed_logging = enable_detailed_logging
        self.execution_stats = {
            "total_plans": 0,
            "total_steps": 0,
            "successful_plans": 0
        }

        print(f"✅ {name} 初始化完成 (PlanAndSolve Agent)")
        if self.enable_detailed_logging:
            print(f"   - 详细日志: 已启用")
            print(f"   - 规划器模板: {'自定义' if custom_prompts.get('planner') else '默认'}")
            print(f"   - 执行器模板: {'自定义' if custom_prompts.get('executor') else '默认'}")

    def run(self, input_text: str, **kwargs) -> str:
        """
        运行 MyPlanAndSolveAgent

        Args:
            input_text: 要解决的问题
            **kwargs: 其他参数

        Returns:
            最终答案
        """
        if self.enable_detailed_logging:
            print("\n" + "=" * 60)
            print(f"🔍 {self.name} - 详细执行日志")
            print("=" * 60)

        # 更新统计信息
        self.execution_stats["total_plans"] += 1

        # 调用父类的 run 方法
        result = super().run(input_text, **kwargs)

        # 更新成功统计
        if result and "无法生成有效的行动计划" not in result:
            self.execution_stats["successful_plans"] += 1

        if self.enable_detailed_logging:
            self._log_execution_summary(result)

        return result

    def _log_execution_summary(self, result: str):
        """记录执行摘要"""
        print("\n" + "-" * 60)
        print("📊 执行摘要")
        print("-" * 60)
        print(f"最终答案: {result}")
        print(f"总计划次数: {self.execution_stats['total_plans']}")
        print(f"成功计划次数: {self.execution_stats['successful_plans']}")
        print(f"成功率: {self.execution_stats['successful_plans'] / max(self.execution_stats['total_plans'], 1) * 100:.1f}%")
        print("-" * 60)

    def get_execution_stats(self) -> Dict[str, any]:
        """
        获取执行统计信息

        Returns:
            包含统计信息的字典
        """
        return self.execution_stats.copy()

    def reset_stats(self):
        """重置统计信息"""
        self.execution_stats = {
            "total_plans": 0,
            "total_steps": 0,
            "successful_plans": 0
        }
        print("✅ 统计信息已重置")


# 便捷函数：创建预配置的 MyPlanAndSolveAgent
def create_default_plan_solve_agent(
    name: str = "我的规划执行助手",
    enable_detailed_logging: bool = False
) -> MyPlanAndSolveAgent:
    """
    创建一个预配置的 MyPlanAndSolveAgent

    Args:
        name: Agent名称
        enable_detailed_logging: 是否启用详细日志

    Returns:
        配置好的 MyPlanAndSolveAgent 实例
    """
    from tiny_agents.core.llm import HelloAgentsLLM

    llm = HelloAgentsLLM()
    agent = MyPlanAndSolveAgent(
        name=name,
        llm=llm,
        enable_detailed_logging=enable_detailed_logging
    )

    return agent
