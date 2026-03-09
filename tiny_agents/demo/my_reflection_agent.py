# my_reflection_agent.py
"""自定义Reflection Agent - 增强版反思与迭代优化智能体"""

from typing import Optional, Dict, Any, Iterator
from tiny_agents.agents.reflection_agent import ReflectionAgent, DEFAULT_PROMPTS, Memory
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.core.config import Config
from tiny_agents.core.message import Message


# 专业领域提示词模板
PROFESSIONAL_PROMPTS = {
    "coding": {
        "initial": """
你是一位经验丰富的程序员。请根据以下要求编写代码：

任务: {task}

要求：
1. 代码应该清晰、易读、有适当的注释
2. 遵循最佳实践和设计模式
3. 考虑边界情况和错误处理
4. 代码的执行效率应该合理
5. 提供完整可运行的代码

请提供完整的代码实现。
""",
        "reflect": """
你是一位代码审查专家。请仔细审查以下代码：

任务: {task}

代码:
{content}

请从以下角度审查：
1. 正确性：代码是否能正确完成任务
2. 可读性：代码结构是否清晰，命名是否合理
3. 健壮性：是否有适当的错误处理
4. 性能：是否有明显的性能问题
5. 安全性：是否存在安全隐患

如果代码已经很好，请回答"无需改进"。否则，请指出具体问题和改进建议。
""",
        "refine": """
请根据反馈意见改进你的代码：

任务: {task}

上一版代码:
{last_attempt}

反馈意见:
{feedback}

请提供改进后的代码，确保解决了所有指出的问题。
"""
    },
    "writing": {
        "initial": """
你是一位专业的作家。请根据以下要求撰写内容：

任务: {task}

要求：
1. 内容准确、结构清晰
2. 语言流畅、表达恰当
3. 符合目标读者的阅读习惯
4. 有吸引力的开头和有力的结尾

请提供完整的撰写内容。
""",
        "reflect": """
你是一位资深编辑。请仔细审查以下文稿：

任务: {task}

文稿:
{content}

请从以下角度审查：
1. 内容质量：信息是否准确、完整
2. 结构逻辑：段落安排是否合理，逻辑是否清晰
3. 语言表达：用词是否准确，句式是否多样化
4. 目标匹配：是否符合目标读者的需求
5. 格式规范：格式是否规范统一

如果文稿已经很好，请回答"无需改进"。否则，请指出具体问题和改进建议。
""",
        "refine": """
请根据反馈意见改进你的文稿：

任务: {task}

上一版文稿:
{last_attempt}

反馈意见:
{feedback}

请提供改进后的文稿，确保解决了所有指出的问题。
"""
    },
    "analysis": {
        "initial": """
你是一位数据分析师。请根据以下要求进行分析：

任务: {task}

要求：
1. 数据准确、分析深入
2. 结论有据可依
3. 提供可行的建议
4. 图文并茂（如适用）

请提供完整的分析报告。
""",
        "reflect": """
你是一位分析报告评审专家。请仔细审查以下分析：

任务: {task}

分析报告:
{content}

请从以下角度审查：
1. 数据准确性：数据来源是否可靠，计算是否正确
2. 分析深度：分析是否透彻，是否有独到见解
3. 结论合理性：结论是否基于数据，逻辑是否严密
4. 建议可行性：建议是否切实可行
5. 报告完整性：是否包含必要的背景、方法和结论

如果分析报告已经很好，请回答"无需改进"。否则，请指出具体问题和改进建议。
""",
        "refine": """
请根据反馈意见改进你的分析报告：

任务: {task}

上一版报告:
{last_attempt}

反馈意见:
{feedback}

请提供改进后的分析报告，确保解决了所有指出的问题。
"""
    }
}


class MyReflectionAgent(ReflectionAgent):
    """
    自定义反思Agent - 增强版

    在原有ReflectionAgent基础上增强：
    1. 支持专业领域模板（编程、写作、分析）
    2. 更详细的迭代日志
    3. 可视化迭代进度
    4. 统计迭代质量指标
    """

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_iterations: int = 3,
        custom_prompts: Optional[Dict[str, str]] = None,
        domain: str = "general"
    ):
        """
        初始化MyReflectionAgent

        Args:
            name: Agent名称
            llm: LLM实例
            system_prompt: 系统提示词
            config: 配置对象
            max_iterations: 最大迭代次数
            custom_prompts: 自定义提示词模板
            domain: 专业领域 (general/coding/writing/analysis)
        """
        # 选择合适的提示词模板
        if domain in PROFESSIONAL_PROMPTS and not custom_prompts:
            selected_prompts = PROFESSIONAL_PROMPTS[domain]
            print(f"✅ 使用 '{domain}' 领域的专业模板")
        else:
            selected_prompts = custom_prompts or DEFAULT_PROMPTS

        super().__init__(
            name=name,
            llm=llm,
            system_prompt=system_prompt,
            config=config,
            max_iterations=max_iterations,
            custom_prompts=selected_prompts
        )

        self.domain = domain
        self.iteration_stats = {
            "total_iterations": 0,
            "improvements_made": 0,
            "feedback_items": []
        }

    def run(self, input_text: str, **kwargs) -> str:
        """
        增强版运行方法 - 带详细统计

        Args:
            input_text: 任务描述
            **kwargs: 其他参数

        Returns:
            最终优化后的结果
        """
        print(f"\n🤖 {self.name} 开始处理任务 (领域: {self.domain})")
        print(f"📋 任务: {input_text}")
        print(f"🔄 最大迭代次数: {self.max_iterations}")

        # 重置统计
        self.iteration_stats = {
            "total_iterations": 0,
            "improvements_made": 0,
            "feedback_items": []
        }

        # 重置记忆
        self.memory = Memory()

        # 1. 初始执行
        print("\n" + "="*60)
        print("🚀 第一阶段：初始尝试")
        print("="*60)
        initial_prompt = self.prompts["initial"].format(task=input_text)
        initial_result = self._get_llm_response(initial_prompt, **kwargs)
        self.memory.add_record("execution", initial_result)
        print(f"✅ 初始尝试完成 (长度: {len(initial_result)} 字符)")

        # 2. 迭代循环：反思与优化
        for i in range(self.max_iterations):
            self.iteration_stats["total_iterations"] = i + 1

            print(f"\n" + "="*60)
            print(f"🔄 第 {i+1}/{self.max_iterations} 轮迭代")
            print("="*60)

            # a. 反思
            print("\n📝 子阶段1: 反思评审")
            last_result = self.memory.get_last_execution()
            reflect_prompt = self.prompts["reflect"].format(
                task=input_text,
                content=last_result
            )
            feedback = self._get_llm_response(reflect_prompt, **kwargs)
            self.memory.add_record("reflection", feedback)
            self.iteration_stats["feedback_items"].append(feedback)
            print(f"✅ 反思完成 (长度: {len(feedback)} 字符)")

            # b. 检查是否需要停止
            if "无需改进" in feedback or "no need for improvement" in feedback.lower():
                print("\n🎉 反思认为结果已无需改进，提前完成任务。")
                break

            # c. 优化
            print("\n⚡ 子阶段2: 优化改进")
            refine_prompt = self.prompts["refine"].format(
                task=input_text,
                last_attempt=last_result,
                feedback=feedback
            )
            refined_result = self._get_llm_response(refine_prompt, **kwargs)
            self.memory.add_record("execution", refined_result)
            self.iteration_stats["improvements_made"] += 1
            print(f"✅ 优化完成 (长度: {len(refined_result)} 字符)")

        final_result = self.memory.get_last_execution()

        # 输出统计信息
        self._print_summary(final_result)

        # 保存到历史记录
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_result, "assistant"))

        return final_result

    def _print_summary(self, result: str):
        """打印执行摘要"""
        print("\n" + "="*60)
        print("📊 执行摘要")
        print("="*60)
        print(f"总迭代轮数: {self.iteration_stats['total_iterations']}")
        print(f"优化次数: {self.iteration_stats['improvements_made']}")
        print(f"最终结果长度: {len(result)} 字符")

        if self.iteration_stats['feedback_items']:
            print(f"\n📝 反思摘要:")
            for i, feedback in enumerate(self.iteration_stats['feedback_items'], 1):
                # 提取关键反馈（前100字）
                summary = feedback[:100] + "..." if len(feedback) > 100 else feedback
                print(f"  轮{i}: {summary}")

        print("="*60)
        print("✅ 任务完成")
        print("="*60)

    def get_stats(self) -> Dict[str, Any]:
        """获取执行统计信息"""
        return self.iteration_stats.copy()

    def get_memory_records(self) -> list:
        """获取所有记忆记录"""
        return self.memory.records.copy()

    def get_reflection_trajectory(self) -> str:
        """获取完整的反思轨迹"""
        return self.memory.get_trajectory()

    def stream_run(self, input_text: str, **kwargs) -> Iterator[str]:
        """
        流式运行方法（简化版）

        由于Reflection Agent需要多轮迭代，流式输出较为复杂。
        这里提供一个基础实现，每轮完成后输出结果。
        """
        print(f"🌊 {self.name} 开始流式处理 (领域: {self.domain})")
        print(f"📋 任务: {input_text}")

        # 重置记忆
        self.memory = Memory()

        # 1. 初始执行
        print("\n--- 初始尝试 ---")
        initial_prompt = self.prompts["initial"].format(task=input_text)
        initial_result = self._get_llm_response(initial_prompt, **kwargs)
        self.memory.add_record("execution", initial_result)
        yield f"[初始尝试]\n{initial_result}\n"

        # 2. 迭代循环
        for i in range(self.max_iterations):
            # 反思
            print(f"\n--- 第 {i+1} 轮反思 ---")
            last_result = self.memory.get_last_execution()
            reflect_prompt = self.prompts["reflect"].format(
                task=input_text,
                content=last_result
            )
            feedback = self._get_llm_response(reflect_prompt, **kwargs)
            self.memory.add_record("reflection", feedback)
            yield f"[反思 {i+1}]\n{feedback}\n"

            # 检查是否停止
            if "无需改进" in feedback or "no need for improvement" in feedback.lower():
                yield "\n[系统] 反思认为结果已无需改进，任务完成。"
                break

            # 优化
            print(f"\n--- 第 {i+1} 轮优化 ---")
            refine_prompt = self.prompts["refine"].format(
                task=input_text,
                last_attempt=last_result,
                feedback=feedback
            )
            refined_result = self._get_llm_response(refine_prompt, **kwargs)
            self.memory.add_record("execution", refined_result)
            yield f"[优化 {i+1}]\n{refined_result}\n"

        final_result = self.memory.get_last_execution()
        yield f"\n[最终结果]\n{final_result}"

        # 保存到历史记录
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_result, "assistant"))

        print(f"\n✅ {self.name} 流式处理完成")


# 便捷函数：创建特定领域的Reflection Agent
def create_agent(name: str, llm: HelloAgentsLLM, domain: str, max_iterations: int = 3) -> MyReflectionAgent:
    """创建特定领域的Reflection Agent"""
    return MyReflectionAgent(
        name=name,
        llm=llm,
        domain=domain,
        max_iterations=max_iterations
    )
