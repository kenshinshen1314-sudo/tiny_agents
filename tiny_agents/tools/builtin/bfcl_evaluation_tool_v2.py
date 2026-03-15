"""
BFCL 评估工具 V2

Berkeley Function Calling Leaderboard (BFCL) 完整评估流程

本工具实现了完整的 BFCL 评估流程：
1. 自动检查和准备 BFCL 数据
2. 运行智能体评估
3. 导出 BFCL 格式结果
4. 调用 BFCL 官方评估工具（可选）
5. 数据聚合和 CSV 生成
6. 评估报告生成

使用示例：
    from tiny_agents import SimpleAgent
    from tiny_agents.tools.builtin import BFCLEvaluationToolV2

    # 创建智能体
    agent = SimpleAgent(name="TestAgent")

    # 创建评估工具
    bfcl_tool = BFCLEvaluationToolV2()

    # 运行评估
    results = bfcl_tool.run(
        agent=agent,
        test_categories=["simple_python"],
        model_name="Qwen/Qwen3-8B",
        partial_eval=True
    )

    print(f"总体准确率: {results['overall_accuracy']:.2%}")
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from ..base import Tool, ToolParameter


class BFCLEvaluationToolV2(Tool):
    """BFCL 完整评估工具 V2

    实现了完整的 BFCL 评估流程，包括：
    - 多类别评估支持
    - partial_eval 标志支持
    - 数据聚合
    - CSV 导出
    - 官方评估工具集成

    支持的评估类别：
    Non-Live (非实时):
        - simple_python: 简单 Python 函数调用
        - simple_java: 简单 Java 函数调用
        - simple_javascript: 简单 JavaScript 函数调用
        - multiple: 多函数调用
        - parallel: 并行函数调用
        - parallel_multiple: 并行多函数调用
        - irrelevance: 无关检测

    Live (实时):
        - live_simple: 实时简单函数调用
        - live_multiple: 实时多函数调用
        - live_parallel: 实时并行函数调用
        - live_parallel_multiple: 实时并行多函数调用
        - live_irrelevance: 实时无关检测
        - live_relevance: 实时相关检测

    Multi-Turn (多轮对话):
        - multi_turn_base: 基础多轮对话
        - multi_turn_miss_func: 缺失函数多轮对话
        - multi_turn_miss_param: 缺失参数多轮对话
        - multi_turn_long_context: 长上下文多轮对话

    Agentic (智能体):
        - memory_kv: KV 存储
        - memory_vector: 向量存储
        - memory_rec_sum: 递归摘要
        - web_search_base: 基础网页搜索
        - web_search_no_snippet: 无摘要网页搜索

    组合类别：
        - "all": 所有类别
        - "all_scoring": 所有计分类别
        - "non_live": 所有 Non-Live 类别
        - "live": 所有 Live 类别
        - "multi_turn": 所有 Multi-Turn 类别
        - "agentic": 所有 Agentic 类别
    """

    # 测试类别映射
    TEST_COLLECTION_MAPPING = {
        "all": [
            "simple_python",
            "simple_java",
            "simple_javascript",
            "multiple",
            "parallel",
            "parallel_multiple",
            "irrelevance",
            "live_simple",
            "live_multiple",
            "live_parallel",
            "live_parallel_multiple",
            "live_irrelevance",
            "live_relevance",
            "multi_turn_base",
            "multi_turn_miss_func",
            "multi_turn_miss_param",
            "multi_turn_long_context",
            "memory_kv",
            "memory_vector",
            "memory_rec_sum",
            "web_search_base",
            "web_search_no_snippet",
        ],
        "all_scoring": [
            "simple_python",
            "simple_java",
            "simple_javascript",
            "multiple",
            "parallel",
            "parallel_multiple",
            "irrelevance",
            "live_simple",
            "live_multiple",
            "live_parallel",
            "live_parallel_multiple",
            "live_irrelevance",
            "live_relevance",
            "multi_turn_base",
            "multi_turn_miss_func",
            "multi_turn_miss_param",
            "multi_turn_long_context",
            "memory_kv",
            "memory_vector",
            "memory_rec_sum",
            "web_search_base",
            "web_search_no_snippet",
        ],
        "non_live": [
            "simple_python",
            "simple_java",
            "simple_javascript",
            "multiple",
            "parallel",
            "parallel_multiple",
            "irrelevance",
        ],
        "live": [
            "live_simple",
            "live_multiple",
            "live_parallel",
            "live_parallel_multiple",
            "live_irrelevance",
            "live_relevance",
        ],
        "multi_turn": [
            "multi_turn_base",
            "multi_turn_miss_func",
            "multi_turn_miss_param",
            "multi_turn_long_context",
        ],
        "agentic": [
            "memory_kv",
            "memory_vector",
            "memory_rec_sum",
            "web_search_base",
            "web_search_no_snippet",
        ],
    }

    def __init__(
        self,
        bfcl_data_dir: Optional[str] = None,
        project_root: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        """初始化 BFCL 评估工具

        Args:
            bfcl_data_dir: BFCL 数据目录路径
            project_root: 项目根目录
            output_dir: 输出目录
        """
        super().__init__(
            name="bfcl_evaluation_v2",
            description=(
                "BFCL 完整评估工具 V2。支持多类别评估、partial_eval 标志、"
                "数据聚合和 CSV 导出。"
            )
        )

        self.project_root = Path(project_root) if project_root else Path.cwd()

        if bfcl_data_dir:
            self.bfcl_data_dir = Path(bfcl_data_dir)
        else:
            self.bfcl_data_dir = (
                self.project_root
                / "temp_gorilla"
                / "berkeley-function-call-leaderboard"
                / "bfcl_eval"
                / "data"
            )

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = self.project_root / "evaluation_results" / "bfcl"

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_parameters(self) -> List[ToolParameter]:
        """获取工具参数定义"""
        return [
            ToolParameter(
                name="agent",
                type="object",
                description="要评估的智能体实例",
                required=True,
            ),
            ToolParameter(
                name="test_categories",
                type="array",
                description="评估类别列表，如 ['simple_python'] 或 ['all_scoring']",
                required=False,
                default=["simple_python"],
            ),
            ToolParameter(
                name="max_samples",
                type="integer",
                description="每个类别评估样本数（默认：5，设为0表示全部）",
                required=False,
                default=5,
            ),
            ToolParameter(
                name="model_name",
                type="string",
                description="模型名称（用于官方评估），如 'Qwen/Qwen3-8B'",
                required=False,
                default="Qwen/Qwen3-8B",
            ),
            ToolParameter(
                name="partial_eval",
                type="boolean",
                description="是否允许部分评估（不要求所有测试条目都有结果）",
                required=False,
                default=True,
            ),
            ToolParameter(
                name="run_official_eval",
                type="boolean",
                description="是否运行 BFCL 官方评估",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="export_csv",
                type="boolean",
                description="是否导出 CSV 文件",
                required=False,
                default=True,
            ),
            ToolParameter(
                name="generate_report",
                type="boolean",
                description="是否生成评估报告",
                required=False,
                default=True,
            ),
        ]

    def _expand_test_categories(
        self, test_categories: List[str]
    ) -> List[str]:
        """展开测试类别

        将组合类别（如 "all"）展开为具体类别列表。

        Args:
            test_categories: 测试类别列表

        Returns:
            展开后的类别列表
        """
        expanded = []
        for category in test_categories:
            if category in self.TEST_COLLECTION_MAPPING:
                expanded.extend(self.TEST_COLLECTION_MAPPING[category])
            else:
                expanded.append(category)
        return list(set(expanded))  # 去重

    def run(
        self,
        agent: Any,
        test_categories: List[str] = ["simple_python"],
        max_samples: int = 5,
        model_name: str = "Qwen/Qwen3-8B",
        partial_eval: bool = True,
        run_official_eval: bool = False,
        export_csv: bool = True,
        generate_report: bool = True,
    ) -> Dict[str, Any]:
        """运行 BFCL 评估

        Args:
            agent: 要评估的智能体
            test_categories: 评估类别列表
            max_samples: 每个类别的最大评估样本数
            model_name: 模型名称
            partial_eval: 是否允许部分评估
            run_official_eval: 是否运行官方评估
            export_csv: 是否导出 CSV
            generate_report: 是否生成报告

        Returns:
            评估结果字典
        """
        from tiny_agents.evaluation import BFCLDataset, BFCLEvaluator
        from tiny_agents.evaluation.benchmarks.bfcl.aggregation import (
            BFCLEvaluationAggregator,
        )
        from tiny_agents.evaluation.benchmarks.bfcl.csv_exporter import (
            BFCLEvaluationCSVExporter,
        )

        print("\n" + "=" * 60)
        print("BFCL 完整评估流程 V2")
        print("=" * 60)

        # 展开测试类别
        expanded_categories = self._expand_test_categories(test_categories)

        print(f"\n配置:")
        print(f"   智能体: {getattr(agent, 'name', 'Unknown')}")
        print(f"   评估类别: {', '.join(expanded_categories)}")
        print(f"   每类样本数: {max_samples if max_samples > 0 else '全部'}")
        print(f"   部分评估: {partial_eval}")
        print(f"   模型名称: {model_name}")

        # 步骤1: 检查 BFCL 数据
        if not self._check_bfcl_data():
            return self._create_error_result("BFCL 数据目录不存在")

        # 创建聚合器
        aggregator = BFCLEvaluationAggregator()

        # 存储所有结果
        all_category_results = {}

        # 步骤2: 对每个类别运行评估
        print("\n" + "=" * 60)
        print("步骤1: 运行智能体评估")
        print("=" * 60)

        for category in expanded_categories:
            print(f"\n📊 评估类别: {category}")

            try:
                # 创建数据集和评估器
                dataset = BFCLDataset(
                    bfcl_data_dir=str(self.bfcl_data_dir), category=category
                )
                evaluator = BFCLEvaluator(dataset=dataset, category=category)

                # 运行评估
                if max_samples > 0:
                    results = evaluator.evaluate(agent, max_samples=max_samples)
                else:
                    results = evaluator.evaluate(agent, max_samples=None)

                # 添加到聚合器
                aggregator.add_category_result(
                    category=category,
                    accuracy=results["overall_accuracy"],
                    correct_count=results["correct_samples"],
                    total_count=results["total_samples"],
                )

                all_category_results[category] = results

                print(
                    f"   准确率: {results['overall_accuracy']:.2%} "
                    f"({results['correct_samples']}/{results['total_samples']})"
                )

            except Exception as e:
                print(f"   ❌ 类别 {category} 评估失败: {e}")
                # 如果不是 partial_eval，抛出异常
                if not partial_eval:
                    raise
                # 否则，记录失败并继续
                all_category_results[category] = {
                    "error": str(e),
                    "overall_accuracy": 0.0,
                }

        # 步骤3: 计算聚合结果
        print("\n" + "=" * 60)
        print("步骤2: 计算聚合结果")
        print("=" * 60)

        aggregated_results = aggregator.get_all_results()

        # 打印汇总
        print(f"\n📈 汇总结果:")
        print(f"   Non-Live: {aggregated_results['non_live']['overall']['display_accuracy']}")
        print(f"   Live: {aggregated_results['live']['overall']['display_accuracy']}")
        print(f"   Multi-Turn: {aggregated_results['multi_turn']['overall']['display_accuracy']}")
        print(f"   Agentic: {aggregated_results['agentic']['overall']['display_accuracy']}")
        print(f"   Overall: {aggregated_results['overall']['display_accuracy']}")

        # 步骤4: 导出 BFCL 格式结果
        print("\n" + "=" * 60)
        print("步骤3: 导出 BFCL 格式结果")
        print("=" * 60)

        for category, results in all_category_results.items():
            if "error" in results:
                continue

            category_output_dir = self.output_dir / "bfcl_format"
            category_output_dir.mkdir(parents=True, exist_ok=True)
            output_file = category_output_dir / f"BFCL_v4_{category}_result.json"

            # 重新创建评估器以导出结果
            dataset = BFCLDataset(
                bfcl_data_dir=str(self.bfcl_data_dir), category=category
            )
            evaluator = BFCLEvaluator(dataset=dataset, category=category)
            evaluator.export_to_bfcl_format(results, output_file)

        # 步骤5: 运行官方评估（可选）
        if run_official_eval:
            self._run_official_evaluation(model_name, expanded_categories, partial_eval)

        # 步骤6: 导出 CSV（可选）
        csv_paths = {}
        if export_csv:
            print("\n" + "=" * 60)
            print("步骤4: 生成 CSV 文件")
            print("=" * 60)

            csv_exporter = BFCLEvaluationCSVExporter(
                output_dir=self.output_dir / "csv"
            )

            # 准备模型结果
            model_results = [
                {
                    "model_name": getattr(agent, "name", "Unknown"),
                    "model_url": "",
                    "aggregated_results": aggregated_results,
                }
            ]

            csv_paths = csv_exporter.export(model_results)

        # 步骤7: 生成报告（可选）
        if generate_report:
            print("\n" + "=" * 60)
            print("步骤5: 生成评估报告")
            print("=" * 60)

            self._generate_report(
                agent,
                expanded_categories,
                all_category_results,
                aggregated_results,
                csv_paths,
            )

        # 返回完整结果
        return {
            "agent_name": getattr(agent, "name", "Unknown"),
            "test_categories": expanded_categories,
            "max_samples": max_samples,
            "partial_eval": partial_eval,
            "category_results": all_category_results,
            "aggregated_results": aggregated_results,
            "csv_paths": {k: str(v) for k, v in csv_paths.items()},
            "overall_accuracy": aggregated_results["overall"]["accuracy"],
        }

    def _check_bfcl_data(self) -> bool:
        """检查 BFCL 数据是否存在"""
        if not self.bfcl_data_dir.exists():
            print(f"\n❌ BFCL 数据目录不存在: {self.bfcl_data_dir}")
            print(f"\n请先克隆 BFCL 仓库：")
            print(f"   git clone --depth 1 https://github.com/ShishirPatil/gorilla.git temp_gorilla")
            return False
        return True

    def _run_official_evaluation(
        self, model_name: str, test_categories: List[str], partial_eval: bool
    ):
        """运行 BFCL 官方评估"""
        print("\n" + "=" * 60)
        print("步骤: 运行 BFCL 官方评估")
        print("=" * 60)

        # 复制结果文件到 BFCL 结果目录
        safe_model_name = model_name.replace("/", "_")
        result_dir = self.project_root / "result" / safe_model_name
        result_dir.mkdir(parents=True, exist_ok=True)

        # 复制所有结果文件
        source_dir = self.output_dir / "bfcl_format"
        if source_dir.exists():
            for file in source_dir.glob("*.json"):
                shutil.copy(file, result_dir / file.name)

        print(f"\n✅ 结果文件已复制到: {result_dir}")

        # 构建命令
        try:
            import os

            os.environ["PYTHONUTF8"] = "1"

            cmd = ["bfcl", "evaluate", "--model", model_name]
            for category in test_categories:
                cmd.extend(["--test-category", category])
            if partial_eval:
                cmd.append("--partial-eval")

            print(f"\n🔄 运行命令: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            if result.stdout:
                print(result.stdout)

            if result.returncode != 0:
                print(f"\n❌ BFCL 评估失败:")
                if result.stderr:
                    print(result.stderr)
            else:
                self._show_official_results(model_name)

        except FileNotFoundError:
            print("\n❌ 未找到 bfcl 命令")
            print("   请先安装: pip install bfcl-eval")
        except Exception as e:
            print(f"\n❌ 运行 BFCL 评估时出错: {e}")

    def _show_official_results(self, model_name: str):
        """展示 BFCL 官方评估结果"""
        print("\n" + "=" * 60)
        print("BFCL 官方评估结果")
        print("=" * 60)

        csv_files = [
            ("总体", self.project_root / "score" / "data_overall.csv"),
            ("Non-Live", self.project_root / "score" / "data_non_live.csv"),
            ("Live", self.project_root / "score" / "data_live.csv"),
        ]

        for name, csv_file in csv_files:
            if csv_file.exists():
                print(f"\n📊 {name}结果:")
                with open(csv_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(content)

    def _generate_report(
        self,
        agent: Any,
        test_categories: List[str],
        category_results: Dict[str, Any],
        aggregated_results: Dict[str, Any],
        csv_paths: Dict[str, str],
    ):
        """生成评估报告"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")

        report = f"""# BFCL 评估报告

**生成时间**: {timestamp}

## 📊 评估概览

- **智能体**: {getattr(agent, 'name', 'Unknown')}
- **评估类别**: {', '.join(test_categories)}
- **总体准确率**: {aggregated_results['overall']['display_accuracy']}

## 📈 详细指标

### Non-Live 测试

| 类别 | 准确率 | 正确数/总数 |
|------|--------|-------------|
| Python Simple | {aggregated_results['non_live']['simple_python']['display_accuracy']} | {aggregated_results['non_live']['simple_python'].get('correct_count', 'N/A')} |
| Java Simple | {aggregated_results['non_live']['simple_java']['display_accuracy']} | {aggregated_results['non_live']['simple_java'].get('correct_count', 'N/A')} |
| JavaScript Simple | {aggregated_results['non_live']['simple_javascript']['display_accuracy']} | {aggregated_results['non_live']['simple_javascript'].get('correct_count', 'N/A')} |
| Multiple | {aggregated_results['non_live']['multiple']['display_accuracy']} | {aggregated_results['non_live']['multiple'].get('correct_count', 'N/A')} |
| Parallel | {aggregated_results['non_live']['parallel']['display_accuracy']} | {aggregated_results['non_live']['parallel'].get('correct_count', 'N/A')} |
| Parallel Multiple | {aggregated_results['non_live']['parallel_multiple']['display_accuracy']} | {aggregated_results['non_live']['parallel_multiple'].get('correct_count', 'N/A')} |
| **Non-Live 总计** | {aggregated_results['non_live']['overall']['display_accuracy']} | - |

### Live 测试

| 类别 | 准确率 | 正确数/总数 |
|------|--------|-------------|
| Live Simple | {aggregated_results['live']['live_simple']['display_accuracy']} | {aggregated_results['live']['live_simple'].get('correct_count', 'N/A')} |
| Live Multiple | {aggregated_results['live']['live_multiple']['display_accuracy']} | {aggregated_results['live']['live_multiple'].get('correct_count', 'N/A')} |
| Live Parallel | {aggregated_results['live']['live_parallel']['display_accuracy']} | {aggregated_results['live']['live_parallel'].get('correct_count', 'N/A')} |
| Live Parallel Multiple | {aggregated_results['live']['live_parallel_multiple']['display_accuracy']} | {aggregated_results['live']['live_parallel_multiple'].get('correct_count', 'N/A')} |
| **Live 总计** | {aggregated_results['live']['overall']['display_accuracy']} | - |

### Multi-Turn 测试

| 类别 | 准确率 | 正确数/总数 |
|------|--------|-------------|
| Base | {aggregated_results['multi_turn']['base']['display_accuracy']} | {aggregated_results['multi_turn']['base'].get('correct_count', 'N/A')} |
| Miss Func | {aggregated_results['multi_turn']['miss_func']['display_accuracy']} | {aggregated_results['multi_turn']['miss_func'].get('correct_count', 'N/A')} |
| Miss Param | {aggregated_results['multi_turn']['miss_param']['display_accuracy']} | {aggregated_results['multi_turn']['miss_param'].get('correct_count', 'N/A')} |
| Long Context | {aggregated_results['multi_turn']['long_context']['display_accuracy']} | {aggregated_results['multi_turn']['long_context'].get('correct_count', 'N/A')} |
| **Multi-Turn 总计** | {aggregated_results['multi_turn']['overall']['display_accuracy']} | - |

### Agentic 测试

| 类别 | 准确率 | 正确数/总数 |
|------|--------|-------------|
| Web Search | {aggregated_results['agentic']['web_search_summary']['display_accuracy']} | - |
| Memory | {aggregated_results['agentic']['memory_summary']['display_accuracy']} | - |
| **Agentic 总计** | {aggregated_results['agentic']['overall']['display_accuracy']} | - |

## 🎯 总体指标

| 指标 | 权重 | 分数 |
|------|------|------|
| Non-Live | 10% | {aggregated_results['non_live']['overall']['display_accuracy']} |
| Live | 10% | {aggregated_results['live']['overall']['display_accuracy']} |
| Irrelevance | 10% | {aggregated_results['irrelevance']['display_accuracy']} |
| Multi-Turn | 30% | {aggregated_results['multi_turn']['overall']['display_accuracy']} |
| Agentic | 40% | {aggregated_results['agentic']['overall']['display_accuracy']} |
| **Overall** | 100% | {aggregated_results['overall']['display_accuracy']} |

"""

        # 添加 CSV 文件路径
        if csv_paths:
            report += "\n## 📁 生成的文件\n\n"
            for name, path in csv_paths.items():
                report += f"- **{name}**: `{path}`\n"

        # 添加建议
        report += "\n## 💡 建议\n\n"
        overall_acc = aggregated_results["overall"]["accuracy"]
        if overall_acc >= 0.9:
            report += "- ✅ 表现优秀！智能体在工具调用方面表现出色。\n"
        elif overall_acc >= 0.7:
            report += "- ⚠️ 表现良好，但仍有提升空间。建议检查错误样本。\n"
        else:
            report += "- ❌ 表现需要改进。建议优化系统提示词和工具调用逻辑。\n"

        # 保存报告
        report_file = (
            self.output_dir / f"bfcl_report_{timestamp_file}.md"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n📄 报告已生成: {report_file}")

    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            "error": error_message,
            "agent_name": "Unknown",
            "test_categories": [],
            "category_results": {},
            "aggregated_results": {},
            "overall_accuracy": 0.0,
        }
