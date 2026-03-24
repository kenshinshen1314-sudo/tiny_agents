"""Service that consolidates task results into the final report."""

from __future__ import annotations

import json

from tiny_agents.agents import ToolAwareSimpleAgent

from models import SummaryState
from config import Configuration
from utils import strip_thinking_tokens
from services.text_processing import strip_tool_calls


class ReportingService:
    """Generates the final structured report."""

    def __init__(self, report_agent: ToolAwareSimpleAgent, config: Configuration) -> None:
        self._agent = report_agent
        self._config = config

    def generate_report(self, state: SummaryState) -> str:
        """Generate a structured report based on completed tasks."""

        tasks_block = []
        for task in state.todo_items:
            summary_block = task.summary or "暂无可用信息"
            sources_block = task.sources_summary or "暂无来源"
            tasks_block.append(
                f"### 任务 {task.id}: {task.title}\n"
                f"- 任务目标：{task.intent}\n"
                f"- 检索查询：{task.query}\n"
                f"- 执行状态：{task.status}\n"
                f"- 任务总结：\n{summary_block}\n"
                f"- 来源概览：\n{sources_block}\n"
            )

        note_references = []
        for task in state.todo_items:
            if task.note_id:
                note_references.append(
                    f"- 任务 {task.id}《{task.title}》：note_id={task.note_id}"
                )

        notes_section = "\n".join(note_references) if note_references else "- 暂无可用任务笔记"

        read_template = json.dumps({"action": "read", "note_id": "<note_id>"}, ensure_ascii=False)
        create_conclusion_template = json.dumps(
            {
                "action": "create",
                "title": f"研究报告：{state.research_topic}",
                "note_type": "conclusion",
                "tags": ["deep_research", "report"],
                "content": "请在此沉淀最终报告要点",
            },
            ensure_ascii=False,
        )

        # 报告结构模板（必须严格遵循，禁止自定义结构）
        # 使用精确的输出格式，强制模型按照这个结构输出
        report_template = """## 输出格式（严格遵守，禁止修改）

按以下5个章节生成完整报告，每一章必须以 "## " 开头：

## 背景概览
[在此输入内容]

## 核心洞见
[在此输入内容]

## 证据与数据
[在此输入内容]

## 风险与挑战
[在此输入内容]

## 参考来源
[在此输入内容]

重要规则：
1. 必须保留 "## 背景概览"、"## 核心洞见"、"## 证据与数据"、"## 风险与挑战"、"## 参考来源" 这5个章节标题
2. 禁止添加任何其他章节（如封面、目录、结论、摘要等）
3. 每个章节必须有实质性内容（至少100字）
4. 禁止只输出摘要或要点，必须输出完整的5章节内容
5. 禁止在输出中包含 "[TOOL_CALL:note:" 这样的工具调用指令
"""

        prompt = (
            f"【研究主题】{state.research_topic}\n\n"
            f"【任务概览】\n{''.join(tasks_block)}\n\n"
            f"【可用任务笔记】\n{notes_section}\n\n"
            f"{report_template}\n\n"
            f"请严格按照上述格式生成完整的5章节研究报告。\n"
            f"\n"
            f"【关键输出要求】（否则任务失败）\n"
            f"1. 直接输出完整的报告内容给你的用户，不要输出摘要或总结\n"
            f"2. 报告必须包含以下5个章节：\n"
            f"   - ## 背景概览\n"
            f"   - ## 核心洞见\n"
            f"   - ## 证据与数据\n"
            f"   - ## 风险与挑战\n"
            f"   - ## 参考来源\n"
            f"3. 每个章节必须有实质性内容（至少100字）\n"
            f"4. 禁止只输出要点摘要，必须是完整的报告\n"
            f"5. 保存报告到笔记可以，但给用户看的输出必须是完整的5章节内容\n"
        )

        response = self._agent.run(prompt)
        self._agent.clear_history()

        report_text = response.strip()
        if self._config.strip_thinking_tokens:
            report_text = strip_thinking_tokens(report_text)

        report_text = strip_tool_calls(report_text).strip()

        return report_text or "报告生成失败，请检查输入。"
