"""
BFCL CSV 输出生成模块

生成 BFCL 官方格式的 CSV 文件，包括：
1. data_overall.csv - 主排行榜
2. data_live.csv - Live 测试类别
3. data_non_live.csv - Non-Live 测试类别
4. data_multi_turn.csv - Multi-Turn 类别
5. data_agentic.csv - Agentic 类别
"""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


# CSV 列头定义
COLUMNS_OVERALL = [
    "Rank",
    "Overall Acc",
    "Model",
    "Link",
    "Cost",
    "Latency",
    "Std",
    "95th Percentile",
    "Non-Live AST Acc",
    "Non-Live Simple Acc",
    "Non-Live Multiple Acc",
    "Non-Live Parallel Acc",
    "Non-Live Parallel Multiple Acc",
    "Live Acc",
    "Live Simple Acc",
    "Live Multiple Acc",
    "Live Parallel Acc",
    "Live Parallel Multiple Acc",
    "Multi Turn Acc",
    "Multi Turn Base Acc",
    "Multi Turn Miss Func Acc",
    "Multi Turn Miss Param Acc",
    "Multi Turn Long Context Acc",
    "Web Search Acc",
    "Web Search Base Acc",
    "Web Search No Snippet Acc",
    "Memory Acc",
    "Memory KV Acc",
    "Memory Vector Acc",
    "Memory Rec Sum Acc",
    "Relevance",
    "Irrelevance",
    "Format Sensitivity Max Delta",
    "Format Sensitivity Std",
    "Organization",
    "License",
]

COLUMNS_NON_LIVE = [
    "Rank",
    "Model",
    "Overall Acc",
    "AST Acc",
    "Simple Acc",
    "Python Simple Acc",
    "Java Simple Acc",
    "JavaScript Simple Acc",
    "Multiple Acc",
    "Parallel Acc",
    "Parallel Multiple Acc",
    "Irrelevance Acc",
]

COLUMNS_LIVE = [
    "Rank",
    "Model",
    "Overall Acc",
    "AST Acc",
    "Simple Acc",
    "Multiple Acc",
    "Parallel Acc",
    "Parallel Multiple Acc",
    "Irrelevance Acc",
    "Relevance Acc",
]

COLUMNS_MULTI_TURN = [
    "Rank",
    "Model",
    "Overall Acc",
    "Base Acc",
    "Miss Func Acc",
    "Miss Param Acc",
    "Long Context Acc",
]

COLUMNS_AGENTIC = [
    "Rank",
    "Model",
    "Overall Acc",
    "Web Search Acc",
    "Web Search Base Acc",
    "Web Search No Snippet Acc",
    "Memory Acc",
    "Memory KV Acc",
    "Memory Vector Acc",
    "Memory Rec Sum Acc",
]


class BFCLEvaluationCSVExporter:
    """BFCL 评估 CSV 导出器

    生成符合 BFCL 官方格式的 CSV 文件。
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """初始化 CSV 导出器

        Args:
            output_dir: 输出目录，默认为当前目录下的 score 文件夹
        """
        if output_dir is None:
            self.output_dir = Path.cwd() / "score"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _format_percentage(self, value: Any) -> str:
        """格式化为百分比字符串

        Args:
            value: 要格式化的值

        Returns:
            格式化后的字符串
        """
        if isinstance(value, str) and value == "N/A":
            return value
        if isinstance(value, (int, float)):
            return f"{value * 100:.2f}%"
        return "N/A"

    def _format_number(self, value: Any, decimals: int = 2) -> str:
        """格式化数字字符串

        Args:
            value: 要格式化的值
            decimals: 小数位数

        Returns:
            格式化后的字符串
        """
        if isinstance(value, str) and value == "N/A":
            return value
        if isinstance(value, (int, float)):
            return f"{value:.{decimals}f}"
        return "N/A"

    def _sort_data(
        self, data: List[List[Any]], sort_column_index: int
    ) -> List[List[Any]]:
        """排序数据

        Args:
            data: 要排序的数据
            sort_column_index: 排序列索引

        Returns:
            排序后的数据
        """
        # 将 "N/A" 排到后面
        sorted_data = sorted(
            data,
            key=lambda x: x[sort_column_index] if x[sort_column_index] != "N/A" else -1,
            reverse=True,
        )
        return sorted_data

    def _add_ranking(self, data: List[List[Any]]) -> List[List[Any]]:
        """添加排名列

        Args:
            data: 要添加排名的数据

        Returns:
            添加排名后的数据
        """
        for i, row in enumerate(data):
            row[0] = str(i + 1)
        return data

    def _prepare_row_overall(
        self,
        model_name: str,
        model_url: str,
        aggregated_results: Dict[str, Any],
        cost: str = "N/A",
        latency_mean: str = "N/A",
        latency_std: str = "N/A",
        latency_p95: str = "N/A",
        org: str = "",
        license: str = "",
        format_sensitivity_max_delta: str = "N/A",
        format_sensitivity_std: str = "N/A",
    ) -> List[str]:
        """准备总体分数行数据

        Args:
            model_name: 模型名称
            model_url: 模型链接
            aggregated_results: 聚合结果
            cost: 成本
            latency_mean: 平均延迟
            latency_std: 延迟标准差
            latency_p95: 95分位延迟
            org: 组织名称
            license: 许可证
            format_sensitivity_max_delta: 格式敏感性最大差值
            format_sensitivity_std: 格式敏感性标准差

        Returns:
            格式化后的行数据
        """
        nl = aggregated_results["non_live"]
        live = aggregated_results["live"]
        mt = aggregated_results["multi_turn"]
        ag = aggregated_results["agentic"]

        return [
            "N/A",  # Rank (稍后填充)
            self._format_percentage(aggregated_results["overall"]["display_accuracy"]),
            model_name,
            model_url,
            self._format_number(cost),
            self._format_number(latency_mean),
            self._format_number(latency_std),
            self._format_number(latency_p95),
            self._format_percentage(nl["summary_ast"]["display_accuracy"]),
            self._format_percentage(nl["simple_ast"]["display_accuracy"]),
            self._format_percentage(nl["multiple"]["display_accuracy"]),
            self._format_percentage(nl["parallel"]["display_accuracy"]),
            self._format_percentage(nl["parallel_multiple"]["display_accuracy"]),
            self._format_percentage(live["overall"]["display_accuracy"]),
            self._format_percentage(live["live_simple"]["display_accuracy"]),
            self._format_percentage(live["live_multiple"]["display_accuracy"]),
            self._format_percentage(live["live_parallel"]["display_accuracy"]),
            self._format_percentage(live["live_parallel_multiple"]["display_accuracy"]),
            self._format_percentage(mt["overall"]["display_accuracy"]),
            self._format_percentage(mt["base"]["display_accuracy"]),
            self._format_percentage(mt["miss_func"]["display_accuracy"]),
            self._format_percentage(mt["miss_param"]["display_accuracy"]),
            self._format_percentage(mt["long_context"]["display_accuracy"]),
            self._format_percentage(ag["web_search_summary"]["display_accuracy"]),
            self._format_percentage(ag["web_search_base"]["display_accuracy"]),
            self._format_percentage(ag["web_search_no_snippet"]["display_accuracy"]),
            self._format_percentage(ag["memory_summary"]["display_accuracy"]),
            self._format_percentage(ag["memory_kv"]["display_accuracy"]),
            self._format_percentage(ag["memory_vector"]["display_accuracy"]),
            self._format_percentage(ag["memory_rec_sum"]["display_accuracy"]),
            self._format_percentage(aggregated_results["relevance"]["display_accuracy"]),
            self._format_percentage(aggregated_results["irrelevance"]["display_accuracy"]),
            self._format_number(format_sensitivity_max_delta),
            self._format_number(format_sensitivity_std),
            org,
            license,
        ]

    def _prepare_row_non_live(
        self, model_name: str, aggregated_results: Dict[str, Any]
    ) -> List[str]:
        """准备 Non-Live 分数行数据

        Args:
            model_name: 模型名称
            aggregated_results: 聚合结果

        Returns:
            格式化后的行数据
        """
        nl = aggregated_results["non_live"]

        return [
            "N/A",  # Rank
            model_name,
            self._format_percentage(nl["overall"]["display_accuracy"]),
            self._format_percentage(nl["summary_ast"]["display_accuracy"]),
            self._format_percentage(nl["simple_ast"]["display_accuracy"]),
            self._format_percentage(nl["simple_python"]["display_accuracy"]),
            self._format_percentage(nl["simple_java"]["display_accuracy"]),
            self._format_percentage(nl["simple_javascript"]["display_accuracy"]),
            self._format_percentage(nl["multiple"]["display_accuracy"]),
            self._format_percentage(nl["parallel"]["display_accuracy"]),
            self._format_percentage(nl["parallel_multiple"]["display_accuracy"]),
            self._format_percentage(nl["irrelevance"]["display_accuracy"]),
        ]

    def _prepare_row_live(
        self, model_name: str, aggregated_results: Dict[str, Any]
    ) -> List[str]:
        """准备 Live 分数行数据

        Args:
            model_name: 模型名称
            aggregated_results: 聚合结果

        Returns:
            格式化后的行数据
        """
        live = aggregated_results["live"]

        return [
            "N/A",  # Rank
            model_name,
            self._format_percentage(live["overall"]["display_accuracy"]),
            self._format_percentage(live["summary_ast"]["display_accuracy"]),
            self._format_percentage(live["live_simple"]["display_accuracy"]),
            self._format_percentage(live["live_multiple"]["display_accuracy"]),
            self._format_percentage(live["live_parallel"]["display_accuracy"]),
            self._format_percentage(live["live_parallel_multiple"]["display_accuracy"]),
            self._format_percentage(live["irrelevance"]["display_accuracy"]),
            self._format_percentage(live["relevance"]["display_accuracy"]),
        ]

    def _prepare_row_multi_turn(
        self, model_name: str, aggregated_results: Dict[str, Any]
    ) -> List[str]:
        """准备 Multi-Turn 分数行数据

        Args:
            model_name: 模型名称
            aggregated_results: 聚合结果

        Returns:
            格式化后的行数据
        """
        mt = aggregated_results["multi_turn"]

        return [
            "N/A",  # Rank
            model_name,
            self._format_percentage(mt["overall"]["display_accuracy"]),
            self._format_percentage(mt["base"]["display_accuracy"]),
            self._format_percentage(mt["miss_func"]["display_accuracy"]),
            self._format_percentage(mt["miss_param"]["display_accuracy"]),
            self._format_percentage(mt["long_context"]["display_accuracy"]),
        ]

    def _prepare_row_agentic(
        self, model_name: str, aggregated_results: Dict[str, Any]
    ) -> List[str]:
        """准备 Agentic 分数行数据

        Args:
            model_name: 模型名称
            aggregated_results: 聚合结果

        Returns:
            格式化后的行数据
        """
        ag = aggregated_results["agentic"]

        return [
            "N/A",  # Rank
            model_name,
            self._format_percentage(ag["overall"]["display_accuracy"]),
            self._format_percentage(ag["web_search_summary"]["display_accuracy"]),
            self._format_percentage(ag["web_search_base"]["display_accuracy"]),
            self._format_percentage(ag["web_search_no_snippet"]["display_accuracy"]),
            self._format_percentage(ag["memory_summary"]["display_accuracy"]),
            self._format_percentage(ag["memory_kv"]["display_accuracy"]),
            self._format_percentage(ag["memory_vector"]["display_accuracy"]),
            self._format_percentage(ag["memory_rec_sum"]["display_accuracy"]),
        ]

    def write_csv(
        self, data: List[List[str]], header: List[str], filename: str, sort_index: int
    ) -> None:
        """写入 CSV 文件

        Args:
            data: 要写入的数据
            header: CSV 列头
            filename: 文件名
            sort_index: 排序列索引
        """
        # 排序数据
        sorted_data = self._sort_data(data, sort_index)

        # 添加排名
        sorted_data = self._add_ranking(sorted_data)

        # 添加列头
        output_data = [header] + sorted_data

        # 写入文件
        file_path = self.output_dir / filename
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(output_data)

        print(f"✅ CSV 文件已生成: {file_path}")

    def export(
        self,
        model_results: List[Dict[str, Any]],
    ) -> Dict[str, Path]:
        """导出所有 CSV 文件

        Args:
            model_results: 模型结果列表，每个元素包含：
                - model_name: 模型名称
                - model_url: 模型链接
                - aggregated_results: 聚合结果
                - cost: 成本（可选）
                - latency_mean: 平均延迟（可选）
                - latency_std: 延迟标准差（可选）
                - latency_p95: 95分位延迟（可选）
                - org: 组织名称（可选）
                - license: 许可证（可选）

        Returns:
            生成的文件路径字典
        """
        data_overall = []
        data_non_live = []
        data_live = []
        data_multi_turn = []
        data_agentic = []

        for result in model_results:
            model_name = result["model_name"]
            model_url = result.get("model_url", "")
            aggregated = result["aggregated_results"]

            data_overall.append(
                self._prepare_row_overall(
                    model_name=model_name,
                    model_url=model_url,
                    aggregated_results=aggregated,
                    cost=result.get("cost", "N/A"),
                    latency_mean=result.get("latency_mean", "N/A"),
                    latency_std=result.get("latency_std", "N/A"),
                    latency_p95=result.get("latency_p95", "N/A"),
                    org=result.get("org", ""),
                    license=result.get("license", ""),
                    format_sensitivity_max_delta=result.get(
                        "format_sensitivity_max_delta", "N/A"
                    ),
                    format_sensitivity_std=result.get(
                        "format_sensitivity_std", "N/A"
                    ),
                )
            )

            data_non_live.append(
                self._prepare_row_non_live(
                    model_name=model_name, aggregated_results=aggregated
                )
            )

            data_live.append(
                self._prepare_row_live(
                    model_name=model_name, aggregated_results=aggregated
                )
            )

            data_multi_turn.append(
                self._prepare_row_multi_turn(
                    model_name=model_name, aggregated_results=aggregated
                )
            )

            data_agentic.append(
                self._prepare_row_agentic(
                    model_name=model_name, aggregated_results=aggregated
                )
            )

        # 写入所有 CSV 文件
        self.write_csv(data_overall, COLUMNS_OVERALL, "data_overall.csv", 1)
        self.write_csv(data_non_live, COLUMNS_NON_LIVE, "data_non_live.csv", 2)
        self.write_csv(data_live, COLUMNS_LIVE, "data_live.csv", 2)
        self.write_csv(
            data_multi_turn, COLUMNS_MULTI_TURN, "data_multi_turn.csv", 2
        )
        self.write_csv(data_agentic, COLUMNS_AGENTIC, "data_agentic.csv", 2)

        return {
            "overall": self.output_dir / "data_overall.csv",
            "non_live": self.output_dir / "data_non_live.csv",
            "live": self.output_dir / "data_live.csv",
            "multi_turn": self.output_dir / "data_multi_turn.csv",
            "agentic": self.output_dir / "data_agentic.csv",
        }
