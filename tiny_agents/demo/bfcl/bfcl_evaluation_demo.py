"""
BFCL 评估流程演示脚本

演示如何使用 BFCLEvaluationToolV2 进行完整的 BFCL 评估。

使用方法:
    python demo/bfcl/bfcl_evaluation_demo.py

环境要求:
    - BFCL 数据目录: temp_gorilla/berkeley-function-call-leaderboard/bfcl_eval/data
    - 或设置 BFCL_DATA_DIR 环境变量
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tiny_agents.agents import SimpleAgent
from tiny_agents.core.llm import HelloAgentsLLM
from tiny_agents.tools.builtin import BFCLEvaluationToolV2


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("BFCL 评估流程演示")
    print("=" * 70)

    # 步骤1: 创建智能体
    print("\n步骤1: 创建智能体")
    print("-" * 70)

    # 使用 HelloAgents LLM
    llm = HelloAgentsLLM()

    # 创建 SimpleAgent
    agent = SimpleAgent(
        name="DemoAgent",
        llm=llm,
        system_prompt="你是一个智能助手，擅长调用工具来解决问题。"
    )

    print(f"✅ 智能体已创建: {agent.name}")

    # 步骤2: 创建 BFCL 评估工具
    print("\n步骤2: 创建 BFCL 评估工具")
    print("-" * 70)

    bfcl_tool = BFCLEvaluationToolV2(
        bfcl_data_dir=str(
            project_root
            / "temp_gorilla/berkeley-function-call-leaderboard/bfcl_eval/data"
        ),
        output_dir=str(project_root / "evaluation_results" / "bfcl"),
    )

    print("✅ BFCL 评估工具已创建")

    # 步骤3: 运行评估
    print("\n步骤3: 运行 BFCL 评估")
    print("-" * 70)
    print("评估配置:")
    print("  - 类别: simple_python (简单 Python 函数调用)")
    print("  - 样本数: 5")
    print("  - 部分评估: 启用")
    print("  - 导出 CSV: 启用")
    print("  - 生成报告: 启用")

    try:
        results = bfcl_tool.run(
            agent=agent,
            test_categories=["simple_python"],
            max_samples=5,
            model_name="DemoAgent",
            partial_eval=True,
            run_official_eval=False,  # 不运行官方评估（需要安装 bfcl-eval）
            export_csv=True,
            generate_report=True,
        )

        # 步骤4: 显示结果
        print("\n" + "=" * 70)
        print("评估完成！")
        print("=" * 70)

        print("\n📊 最终结果:")
        print(f"  总体准确率: {results['overall_accuracy']:.2%}")

        if "aggregated_results" in results:
            agg = results["aggregated_results"]
            print("\n📈 分类结果:")
            print(f"  Non-Live: {agg['non_live']['overall']['display_accuracy']}")
            print(f"  Live: {agg['live']['overall']['display_accuracy']}")
            print(f"  Multi-Turn: {agg['multi_turn']['overall']['display_accuracy']}")
            print(f"  Agentic: {agg['agentic']['overall']['display_accuracy']}")
            print(f"  Overall: {agg['overall']['display_accuracy']}")

        if "csv_paths" in results and results["csv_paths"]:
            print("\n📁 生成的文件:")
            for name, path in results["csv_paths"].items():
                print(f"  {name}: {path}")

        print("\n💡 提示:")
        print("  - 查看 evaluation_results/bfcl/ 目录获取详细结果")
        print("  - 报告文件包含详细的评估指标和建议")

    except Exception as e:
        print(f"\n❌ 评估失败: {e}")
        print("\n💡 请检查:")
        print("  1. BFCL 数据目录是否存在")
        print("  2. 智能体配置是否正确")
        print("  3. LLM 服务是否可用")


if __name__ == "__main__":
    main()
