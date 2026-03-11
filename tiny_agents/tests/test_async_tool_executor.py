# test_async_tool_executor.py
"""AsyncToolExecutor 测试脚本 - 异步工具执行器测试"""

import asyncio
from dotenv import load_dotenv
from tiny_agents.tools.registry import ToolRegistry
from tiny_agents.tools.async_tool_executor import AsyncToolExecutor
from tiny_agents.tools.builtin.calculator import CalculatorTool

# 加载环境变量
load_dotenv()

# ==================== 辅助函数 ====================

def create_mock_search_tool():
    """创建模拟搜索工具"""
    def mock_search(query: str) -> str:
        return f"搜索结果：关于 '{query}' 的相关信息..."

    return mock_search

def create_mock_delay_tool():
    """创建模拟延时工具（用于测试并行）"""
    def mock_delay(input_data: str) -> str:
        import time
        time.sleep(0.5)  # 模拟耗时操作
        return f"处理完成: {input_data}"

    return mock_delay

# ==================== 测试1：基础异步工具执行 ====================
print("\n" + "="*80)
print("测试1：基础异步工具执行")
print("="*80)

async def test_basic_async_execution():
    """测试基础的异步工具执行"""

    # 创建工具注册表并注册工具
    registry = ToolRegistry()
    calculator = CalculatorTool()
    registry.register_tool(calculator)

    # 为了兼容性，也注册为函数工具
    def my_calculator(expr: str) -> str:
        result = calculator.run({"input": expr})
        return result.text if hasattr(result, 'text') else str(result)

    registry.register_function(my_calculator, name="my_calculator", description="计算器工具")

    # 创建异步执行器
    executor = AsyncToolExecutor(registry)

    # 异步执行单个工具
    print("\n--- 执行单个工具 ---")
    result = await executor.execute_tool_async("my_calculator", "15 + 25")
    print(f"计算结果: {result}")

    # 清理
    del executor

# 运行测试1
asyncio.run(test_basic_async_execution())

# ==================== 测试2：并行执行多个工具 ====================
print("\n" + "="*80)
print("测试2：并行执行多个工具")
print("="*80)

async def test_parallel_execution():
    """测试并行执行多个工具"""

    # 创建工具注册表
    registry = ToolRegistry()
    calculator = CalculatorTool()
    registry.register_tool(calculator)

    # 注册多个函数工具
    def my_calculator(expr: str) -> str:
        result = calculator.run({"input": expr})
        return result.text if hasattr(result, 'text') else str(result)

    def search_tool(query: str) -> str:
        return f"搜索结果：{query} 的相关信息..."

    def upper_case(input_data: str) -> str:
        return f"大写转换: {input_data.upper()}"

    registry.register_function(my_calculator, name="my_calculator", description="计算器")
    registry.register_function(search_tool, name="search", description="搜索工具")
    registry.register_function(upper_case, name="upper_case", description="大写转换")

    # 创建异步执行器
    executor = AsyncToolExecutor(registry, max_workers=3)

    # 定义并行任务
    tasks = [
        {"tool_name": "my_calculator", "input_data": "10 + 20"},
        {"tool_name": "my_calculator", "input_data": "5 * 8"},
        {"tool_name": "my_calculator", "input_data": "100 / 4"},
    ]

    # 并行执行
    print("\n--- 并行执行3个计算任务 ---")
    results = await executor.execute_tools_parallel(tasks)

    print("\n--- 执行结果 ---")
    for i, (task, result) in enumerate(zip(tasks, results)):
        print(f"任务{i+1} [{task['tool_name']}]: {task['input_data']}")
        print(f"  结果: {result}")

    # 清理
    del executor

# 运行测试2
asyncio.run(test_parallel_execution())

# ==================== 测试3：混合不同类型的工具 ====================
print("\n" + "="*80)
print("测试3：混合不同类型的工具")
print("="*80)

async def test_mixed_tools():
    """测试混合不同类型的工具"""

    registry = ToolRegistry()
    calculator = CalculatorTool()
    registry.register_tool(calculator)

    def my_calculator(expr: str) -> str:
        result = calculator.run({"input": expr})
        return result.text if hasattr(result, 'text') else str(result)

    def mock_search(query: str) -> str:
        return f"找到关于 '{query}' 的 {len(query)} 条相关信息"

    def mock_reverse(text: str) -> str:
        return f"反转结果: {text[::-1]}"

    registry.register_function(my_calculator, name="calc", description="计算器")
    registry.register_function(mock_search, name="search", description="搜索")
    registry.register_function(mock_reverse, name="reverse", description="反转")

    executor = AsyncToolExecutor(registry, max_workers=3)

    tasks = [
        {"tool_name": "calc", "input_data": "2 * 3 * 4"},
        {"tool_name": "search", "input_data": "Python编程"},
        {"tool_name": "reverse", "input_data": "Hello World"},
    ]

    print("\n--- 执行混合任务 ---")
    results = await executor.execute_tools_parallel(tasks)

    print("\n--- 执行结果 ---")
    for i, (task, result) in enumerate(zip(tasks, results)):
        print(f"任务{i+1} [{task['tool_name']}]: {task['input_data']}")
        print(f"  结果: {result}")

    del executor

# 运行测试3
asyncio.run(test_mixed_tools())

# ==================== 测试4：大批量并行任务 ====================
print("\n" + "="*80)
print("测试4：大批量并行任务")
print("="*80)

async def test_large_batch():
    """测试大批量并行任务"""

    registry = ToolRegistry()

    # 注册简单的处理工具
    def process_task(input_data: str) -> str:
        task_num = input_data.split("_")[1]
        return f"任务{task_num}完成"

    registry.register_function(process_task, name="processor", description="处理器")

    executor = AsyncToolExecutor(registry, max_workers=5)

    # 创建10个任务
    tasks = [{"tool_name": "processor", "input_data": f"task_{i}"} for i in range(1, 11)]

    print(f"\n--- 并行执行 {len(tasks)} 个任务 ---")
    results = await executor.execute_tools_parallel(tasks)

    print(f"\n完成度: {len(results)}/{len(tasks)}")
    print(f"前3个结果: {results[:3]}")

    del executor

# 运行测试4
asyncio.run(test_large_batch())

# ==================== 测试5：自定义最大工作线程数 ====================
print("\n" + "="*80)
print("测试5：自定义最大工作线程数")
print("="*80)

async def test_custom_max_workers():
    """测试自定义最大工作线程数"""

    registry = ToolRegistry()
    calculator = CalculatorTool()
    registry.register_tool(calculator)

    def my_calculator(expr: str) -> str:
        result = calculator.run({"input": expr})
        return result.text if hasattr(result, 'text') else str(result)

    registry.register_function(my_calculator, name="calc", description="计算器")

    # 使用不同的 max_workers
    for max_workers in [1, 2, 4]:
        print(f"\n--- max_workers={max_workers} ---")
        executor = AsyncToolExecutor(registry, max_workers=max_workers)

        tasks = [
            {"tool_name": "calc", "input_data": f"{i} + {i+1}"}
            for i in range(4)
        ]

        results = await executor.execute_tools_parallel(tasks)
        print(f"完成任务数: {len(results)}")

        del executor

# 运行测试5
asyncio.run(test_custom_max_workers())

# ==================== 测试6：空任务列表 ====================
print("\n" + "="*80)
print("测试6：空任务列表")
print("="*80)

async def test_empty_tasks():
    """测试空任务列表"""

    registry = ToolRegistry()
    executor = AsyncToolExecutor(registry)

    print("\n--- 执行空任务列表 ---")
    results = await executor.execute_tools_parallel([])

    print(f"结果数量: {len(results)}")
    print(f"结果内容: {results}")

    del executor

# 运行测试6
asyncio.run(test_empty_tasks())

# ==================== 测试7：工具不存在的情况 ====================
print("\n" + "="*80)
print("测试7：工具不存在的情况")
print("="*80)

async def test_nonexistent_tool():
    """测试工具不存在的情况"""

    registry = ToolRegistry()
    executor = AsyncToolExecutor(registry)

    print("\n--- 尝试执行不存在的工具 ---")
    try:
        result = await executor.execute_tool_async("nonexistent_tool", "test input")
        print(f"结果: {result}")
    except Exception as e:
        print(f"捕获异常: {e}")

    del executor

# 运行测试7
asyncio.run(test_nonexistent_tool())

# ==================== 测试8：并行执行中的错误处理 ====================
print("\n" + "="*80)
print("测试8：并行执行中的错误处理")
print("="*80)

async def test_error_in_parallel():
    """测试并行执行中的错误处理"""

    registry = ToolRegistry()
    calculator = CalculatorTool()
    registry.register_tool(calculator)

    def my_calculator(expr: str) -> str:
        try:
            result = calculator.run({"input": expr})
            return result.text if hasattr(result, 'text') else str(result)
        except:
            return f"计算错误: {expr}"

    def failing_tool(input_data: str) -> str:
        raise ValueError("这是一个故意抛出的错误")

    def working_tool(input_data: str) -> str:
        return f"正常工作: {input_data}"

    registry.register_function(my_calculator, name="calc", description="计算器")
    registry.register_function(failing_tool, name="failing", description="失败工具")
    registry.register_function(working_tool, name="working", description="正常工具")

    executor = AsyncToolExecutor(registry, max_workers=3)

    tasks = [
        {"tool_name": "calc", "input_data": "10 + 20"},
        {"tool_name": "failing", "input_data": "test"},
        {"tool_name": "working", "input_data": "test input"},
    ]

    print("\n--- 执行包含失败的任务 ---")
    try:
        results = await executor.execute_tools_parallel(tasks)
        print(f"完成数: {len([r for r in results if r])}")
        for i, result in enumerate(results):
            print(f"任务{i+1}: {str(result)[:100]}...")
    except Exception as e:
        print(f"捕获异常: {e}")

    del executor

# 运行测试8
asyncio.run(test_error_in_parallel())

# ==================== 测试9：延时工具并行执行 ====================
print("\n" + "="*80)
print("测试9：延时工具并行执行")
print("="*80)

async def test_delayed_tools():
    """测试延时工具的并行执行"""

    import time

    registry = ToolRegistry()

    def delay_tool(input_data: str) -> str:
        delay = float(input_data.split(":")[1])
        time.sleep(delay)
        return f"延时 {delay}秒完成"

    registry.register_function(delay_tool, name="delay", description="延时工具")

    executor = AsyncToolExecutor(registry, max_workers=3)

    tasks = [
        {"tool_name": "delay", "input_data": "delay:0.3"},
        {"tool_name": "delay", "input_data": "delay:0.2"},
        {"tool_name": "delay", "input_data": "delay:0.1"},
    ]

    print("\n--- 并行执行3个延时任务 ---")
    print("预期时间约0.3秒（并行），而非0.6秒（串行）")

    import time
    start_time = time.time()
    results = await executor.execute_tools_parallel(tasks)
    elapsed = time.time() - start_time

    print(f"\n实际用时: {elapsed:.2f}秒")
    print(f"执行结果: {results}")

    del executor

# 运行测试9
asyncio.run(test_delayed_tools())

# ==================== 测试10：顺序执行对比 ====================
print("\n" + "="*80)
print("测试10：顺序执行对比")
print("="*80)

async def test_sequential_vs_parallel():
    """对比顺序执行和并行执行"""

    import time

    registry = ToolRegistry()

    def task_tool(input_data: str) -> str:
        time.sleep(0.2)
        return f"{input_data} 完成"

    registry.register_function(task_tool, name="task", description="任务工具")

    executor = AsyncToolExecutor(registry, max_workers=3)

    tasks = [
        {"tool_name": "task", "input_data": f"任务{i}"}
        for i in range(1, 4)
    ]

    # 并行执行
    print("\n--- 并行执行 ---")
    start_time = time.time()
    parallel_results = await executor.execute_tools_parallel(tasks)
    parallel_time = time.time() - start_time
    print(f"用时: {parallel_time:.2f}秒")
    print(f"结果: {parallel_results}")

    # 顺序执行对比
    print("\n--- 顺序执行（对比） ---")
    start_time = time.time()
    sequential_results = []
    for task in tasks:
        result = await executor.execute_tool_async(task["tool_name"], task["input_data"])
        sequential_results.append(result)
    sequential_time = time.time() - start_time
    print(f"用时: {sequential_time:.2f}秒")
    print(f"结果: {sequential_results}")

    print(f"\n性能提升: {sequential_time/parallel_time:.2f}x")

    del executor

# 运行测试10
asyncio.run(test_sequential_vs_parallel())

# ==================== 测试11：计算器密集型任务 ====================
print("\n" + "="*80)
print("测试11：计算器密集型任务")
print("="*80)

async def test_calculator_intensive():
    """测试计算器密集型任务"""

    registry = ToolRegistry()
    calculator = CalculatorTool()
    registry.register_tool(calculator)

    def my_calculator(expr: str) -> str:
        result = calculator.run({"input": expr})
        return result.text if hasattr(result, 'text') else str(result)

    registry.register_function(my_calculator, name="calc", description="计算器")

    executor = AsyncToolExecutor(registry, max_workers=5)

    # 创建10个计算任务
    tasks = [
        {"tool_name": "calc", "input_data": f"{i} * {i+1} + {i+2}"}
        for i in range(10)
    ]

    print(f"\n--- 并行执行 {len(tasks)} 个计算任务 ---")
    results = await executor.execute_tools_parallel(tasks)

    print(f"\n完成: {len(results)}/{len(tasks)}")
    print("\n部分结果:")
    for i in range(min(5, len(results))):
        print(f"  任务{i+1}: {results[i]}")

    del executor

# 运行测试11
asyncio.run(test_calculator_intensive())

# ==================== 测试12：不同返回类型 ====================
print("\n" + "="*80)
print("测试12：不同返回类型")
print("="*80)

async def test_different_return_types():
    """测试不同类型的返回值"""

    registry = ToolRegistry()

    def int_tool(input_data: str) -> str:
        return "42"

    def float_tool(input_data: str) -> str:
        return "3.14159"

    def json_tool(input_data: str) -> str:
        return '{"status": "success", "value": 100}'

    def list_tool(input_data: str) -> str:
        return "[1, 2, 3, 4, 5]"

    registry.register_function(int_tool, name="int_tool", description="整数工具")
    registry.register_function(float_tool, name="float_tool", description="浮点工具")
    registry.register_function(json_tool, name="json_tool", description="JSON工具")
    registry.register_function(list_tool, name="list_tool", description="列表工具")

    executor = AsyncToolExecutor(registry, max_workers=4)

    tasks = [
        {"tool_name": "int_tool", "input_data": "test"},
        {"tool_name": "float_tool", "input_data": "test"},
        {"tool_name": "json_tool", "input_data": "test"},
        {"tool_name": "list_tool", "input_data": "test"},
    ]

    print("\n--- 执行不同类型的工具 ---")
    results = await executor.execute_tools_parallel(tasks)

    print("\n--- 执行结果 ---")
    for i, (task, result) in enumerate(zip(tasks, results)):
        print(f"{task['tool_name']}: {result}")

    del executor

# 运行测试12
asyncio.run(test_different_return_types())

# ==================== 测试13：多次运行同一工具 ====================
print("\n" + "="*80)
print("测试13：多次运行同一工具")
print("="*80)

async def test_repeated_tool_calls():
    """测试多次调用同一工具"""

    registry = ToolRegistry()
    calculator = CalculatorTool()
    registry.register_tool(calculator)

    def my_calculator(expr: str) -> str:
        result = calculator.run({"input": expr})
        return result.text if hasattr(result, 'text') else str(result)

    registry.register_function(my_calculator, name="calc", description="计算器")

    executor = AsyncToolExecutor(registry, max_workers=3)

    # 多次调用同一工具，但输入不同
    tasks = [
        {"tool_name": "calc", "input_data": f"{i} + {i*2}"}
        for i in range(5)
    ]

    print(f"\n--- {len(tasks)}次调用计算器 ---")
    results = await executor.execute_tools_parallel(tasks)

    print("\n--- 执行结果 ---")
    for i, (task, result) in enumerate(zip(tasks, results)):
        print(f"{task['input_data']} = {result}")

    del executor

# 运行测试13
asyncio.run(test_repeated_tool_calls())

# ==================== 测试14：资源清理测试 ====================
print("\n" + "="*80)
print("测试14：资源清理测试")
print("="*80)

async def test_cleanup():
    """测试资源清理"""

    import gc

    registry = ToolRegistry()

    def dummy_tool(input_data: str) -> str:
        return f"处理: {input_data}"

    registry.register_function(dummy_tool, name="dummy", description="测试工具")

    print("\n--- 创建多个执行器实例 ---")
    executors = []
    for i in range(3):
        exec = AsyncToolExecutor(registry, max_workers=2)
        executors.append(exec)
        print(f"创建执行器 {i+1}")

    # 使用后删除
    print("\n--- 清理执行器 ---")
    for i, exec in enumerate(executors):
        del exec
        print(f"删除执行器 {i+1}")

    # 垃圾回收
    gc.collect()
    print("\n✅ 资源清理完成")

# 运行测试14
asyncio.run(test_cleanup())

# ==================== 测试15：实际应用场景模拟 ====================
print("\n" + "="*80)
print("测试15：实际应用场景模拟")
print("="*80)

async def test_real_world_scenario():
    """模拟真实应用场景"""

    registry = ToolRegistry()
    calculator = CalculatorTool()
    registry.register_tool(calculator)

    def my_calculator(expr: str) -> str:
        result = calculator.run({"input": expr})
        return result.text if hasattr(result, 'text') else str(result)

    def search_data(query: str) -> str:
        # 模拟数据搜索
        data = {
            "用户数": "1000",
            "收入": "50000",
            "成本": "30000"
        }
        return f"{query}: {data.get(query, '未找到')}"

    def format_report(input_data: str) -> str:
        return f"[报告] {input_data}"

    def save_result(input_data: str) -> str:
        return f"[保存] {input_data}"

    registry.register_function(my_calculator, name="calc", description="计算器")
    registry.register_function(search_data, name="search", description="数据搜索")
    registry.register_function(format_report, name="format", description="格式化")
    registry.register_function(save_result, name="save", description="保存")

    executor = AsyncToolExecutor(registry, max_workers=4)

    # 模拟业务流程：搜索数据 -> 计算 -> 格式化 -> 保存
    tasks = [
        {"tool_name": "search", "input_data": "用户数"},
        {"tool_name": "search", "input_data": "收入"},
        {"tool_name": "calc", "input_data": "50000 - 30000"},
        {"tool_name": "format", "input_data": "利润分析"},
    ]

    print("\n--- 执行业务流程 ---")
    results = await executor.execute_tools_parallel(tasks)

    print("\n--- 业务流程结果 ---")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result}")

    del executor

# 运行测试15
asyncio.run(test_real_world_scenario())

# ==================== 总结统计 ====================
print("\n" + "="*80)
print("测试总结")
print("="*80)

print("\n✅ 所有测试完成！")
print("\n测试覆盖:")
print("  1. 基础异步工具执行")
print("  2. 并行执行多个工具")
print("  3. 混合不同类型的工具")
print("  4. 大批量并行任务")
print("  5. 自定义最大工作线程数")
print("  6. 空任务列表")
print("  7. 工具不存在的情况")
print("  8. 并行执行中的错误处理")
print("  9. 延时工具并行执行")
print("  10. 顺序执行对比")
print("  11. 计算器密集型任务")
print("  12. 不同返回类型")
print("  13. 多次运行同一工具")
print("  14. 资源清理测试")
print("  15. 实际应用场景模拟")

print("\n" + "="*80)
print("\n提示: 所有测试都使用 asyncio.run() 运行")
print("在实际使用中，你可以在异步函数中直接使用 await")
print("\n" + "="*80)
