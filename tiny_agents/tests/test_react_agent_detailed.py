"""
详细测试 ReAct Agent 调用链
验证计划文档中描述的各个测试用例
"""

from dotenv import load_dotenv
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.tools.registry import ToolRegistry
from tiny_agents.demo.my_react_agent import MyReActAgent

# 加载环境变量
load_dotenv()


def test_math_calculation():
    """测试用例 1: 数学计算问题"""
    print("\n" + "="*60)
    print("测试用例 1: 数学计算问题")
    print("="*60)

    # 阶段 1: 初始化
    print("\n[阶段 1: 初始化]")
    llm = HelloAgentsLLM()
    print(f"✅ HelloAgentsLLM 初始化完成")
    print(f"   - Provider: {llm.provider}")
    print(f"   - Model: {llm.model}")
    print(f"   - Base URL: {llm.base_url}")

    tool_registry = ToolRegistry()
    print(f"✅ ToolRegistry 初始化完成")

    from tiny_agents.tools.builtin.calculator import calculate
    tool_registry.register_function("calculate", "执行数学计算，支持基本的四则运算", calculate)
    print(f"✅ 计算器工具注册成功")

    agent = MyReActAgent(
        name="我的推理行动助手",
        llm=llm,
        tool_registry=tool_registry,
        max_steps=5,
    )
    print(f"✅ MyReActAgent 初始化完成")
    print(f"   - Max Steps: {agent.max_steps}")
    print(f"   - Prompt Template: {len(agent.prompt_template)} 字符")

    # 阶段 2: 执行测试
    print("\n[阶段 2: 执行测试]")
    math_question = "(25 + 15) * 3 - 8"
    print(f"问题: {math_question}")

    result = agent.run(f"请帮我计算：{math_question} 的结果是多少？")
    print(f"\n结果: {result}")

    return agent, result


def test_search_question():
    """测试用例 2: 信息搜索问题"""
    print("\n" + "="*60)
    print("测试用例 2: 信息搜索问题")
    print("="*60)

    llm = HelloAgentsLLM()
    tool_registry = ToolRegistry()

    from tiny_agents.tools.builtin.search import search
    tool_registry.register_function("search", "搜索互联网信息", search)
    print(f"✅ 搜索工具注册成功")

    agent = MyReActAgent(
        name="搜索助手",
        llm=llm,
        tool_registry=tool_registry,
        max_steps=5,
    )

    search_question = "Python编程语言是什么时候发布的？请告诉我具体的年份。"
    print(f"问题: {search_question}")

    result = agent.run(search_question)
    print(f"\n结果: {result}")

    return agent, result


def test_complex_reasoning():
    """测试用例 3: 复合推理问题"""
    print("\n" + "="*60)
    print("测试用例 3: 复合推理问题")
    print("="*60)

    llm = HelloAgentsLLM()
    tool_registry = ToolRegistry()

    from tiny_agents.tools.builtin.calculator import calculate
    tool_registry.register_function("calculate", "执行数学计算", calculate)
    print(f"✅ 计算器工具注册成功")

    agent = MyReActAgent(
        name="复合推理助手",
        llm=llm,
        tool_registry=tool_registry,
        max_steps=5,
    )

    complex_question = "如果一个班级有30个学生，其中60%是女生，那么男生有多少人？请先计算女生人数，再计算男生人数。"
    print(f"问题: {complex_question}")

    result = agent.run(complex_question)
    print(f"\n结果: {result}")

    return agent, result


def test_custom_prompt():
    """测试用例 4: 自定义提示词测试"""
    print("\n" + "="*60)
    print("测试用例 4: 自定义提示词测试")
    print("="*60)

    llm = HelloAgentsLLM()
    tool_registry = ToolRegistry()

    from tiny_agents.tools.builtin.calculator import calculate
    tool_registry.register_function("calculate", "执行数学计算", calculate)
    print(f"✅ 计算器工具注册成功")

    custom_prompt = """你是一个数学专家AI助手。

可用工具：{tools}

请按以下格式回应：
Thought: [你的思考]
Action: [tool_name[input] 或 Finish[答案]]

问题：{question}
历史：{history}

开始："""

    custom_agent = MyReActAgent(
        name="数学专家助手",
        llm=llm,
        tool_registry=tool_registry,
        max_steps=3,
        custom_prompt=custom_prompt
    )
    print(f"✅ 自定义提示词 Agent 初始化完成")
    print(f"   - Max Steps: {custom_agent.max_steps} (注意：这里是 3)")

    math_question = "计算 15 × 8 + 32 ÷ 4 的结果"
    print(f"问题: {math_question}")

    result = custom_agent.run(math_question)
    print(f"\n结果: {result}")

    return custom_agent, result


if __name__ == "__main__":
    print("="*60)
    print("ReAct Agent 详细测试 - 验证调用链")
    print("="*60)

    try:
        # 测试 1: 数学计算
        agent1, result1 = test_math_calculation()
        print(f"\n✅ 测试 1 完成")

        # 测试 2: 信息搜索
        agent2, result2 = test_search_question()
        print(f"\n✅ 测试 2 完成")

        # 测试 3: 复合推理
        agent3, result3 = test_complex_reasoning()
        print(f"\n✅ 测试 3 完成")

        # 测试 4: 自定义提示词
        agent4, result4 = test_custom_prompt()
        print(f"\n✅ 测试 4 完成")

        print("\n" + "="*60)
        print("🎉 所有测试完成！")
        print("="*60)

        # 测试用例对比表
        print("\n" + "="*60)
        print("测试用例对比")
        print("="*60)
        print("| 测试用例 | 问题类型 | 工具调用 | 特点 |")
        print("|---------|---------|---------|------|")
        print("| 测试1 | 数学计算 | calculate | 单次工具调用，直接得出结果 |")
        print("| 测试2 | 信息搜索 | search | 搜索工具获取外部信息 |")
        print("| 测试3 | 复合推理 | calculate × 2 | 多步骤推理，需要多次工具调用 |")
        print("| 测试4 | 自定义提示词 | calculate | 使用自定义提示词模板，max_steps=3 |")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
