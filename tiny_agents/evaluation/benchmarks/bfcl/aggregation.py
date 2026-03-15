"""
BFCL 数据聚合模块

实现 BFCL 官方评估的数据聚合逻辑，包括：
1. 加权平均计算
2. 非加权平均计算
3. 百分比加权平均计算
4. 总体指标计算
"""

from typing import List, Dict, Any, Optional, Tuple


class BFCLEvaluationAggregator:
    """BFCL 评估数据聚合器

    负责将各个类别的评估结果聚合成总体指标。

    Overall 指标权重分配：
    - Non-Live: 10%
    - Live: 10%
    - Irrelevance: 10%
    - Multi-Turn: 30%
    - Agentic: 40%
    """

    # Overall 指标权重
    OVERALL_WEIGHTS = {
        "non_live": 0.10,
        "live": 0.10,
        "irrelevance": 0.10,
        "multi_turn": 0.30,
        "agentic": 0.40,
    }

    # Non-Live 测试类别
    NON_LIVE_CATEGORIES = [
        "simple_python",
        "simple_java",
        "simple_javascript",
        "multiple",
        "parallel",
        "parallel_multiple",
        "irrelevance",
    ]

    # Live 测试类别
    LIVE_CATEGORIES = [
        "live_simple",
        "live_multiple",
        "live_parallel",
        "live_parallel_multiple",
        "live_irrelevance",
        "live_relevance",
    ]

    # Multi-Turn 测试类别
    MULTI_TURN_CATEGORIES = [
        "multi_turn_base",
        "multi_turn_miss_func",
        "multi_turn_miss_param",
        "multi_turn_long_context",
    ]

    # Agentic 测试类别
    AGENTIC_CATEGORIES = [
        "memory_kv",
        "memory_vector",
        "memory_rec_sum",
        "web_search_base",
        "web_search_no_snippet",
    ]

    def __init__(self):
        """初始化聚合器"""
        self.category_results: Dict[str, Dict[str, Any]] = {}

    def add_category_result(
        self,
        category: str,
        accuracy: float,
        correct_count: int,
        total_count: int,
    ) -> None:
        """添加单个类别的评估结果

        Args:
            category: 测试类别名称
            accuracy: 准确率
            correct_count: 正确样本数
            total_count: 总样本数
        """
        self.category_results[category] = {
            "accuracy": accuracy,
            "correct_count": correct_count,
            "total_count": total_count,
        }

    def calculate_weighted_accuracy(
        self,
        accuracy_dict_list: List[Dict[str, Any]],
        display_na_if_missing: bool = True,
    ) -> Dict[str, Any]:
        """计算加权平均准确率

        权重由每个类别的样本数量决定。

        Args:
            accuracy_dict_list: 准确率字典列表
            display_na_if_missing: 如果类别缺失是否显示 N/A

        Returns:
            包含 accuracy, total_count, display_accuracy 的字典
        """
        has_na = False
        total_count = 0
        total_accuracy = 0.0

        for accuracy_dict in accuracy_dict_list:
            accuracy = accuracy_dict["accuracy"]
            count = accuracy_dict["total_count"]
            if accuracy_dict.get("display_accuracy") == "N/A":
                has_na = True

            total_count += count
            total_accuracy += accuracy * count

        result = {
            "accuracy": total_accuracy / total_count if total_count > 0 else 0.0,
            "total_count": total_count,
        }

        if has_na and display_na_if_missing:
            result["display_accuracy"] = "N/A"
        else:
            result["display_accuracy"] = result["accuracy"]

        return result

    def calculate_unweighted_accuracy(
        self,
        accuracy_dict_list: List[Dict[str, Any]],
        display_na_if_missing: bool = True,
    ) -> Dict[str, Any]:
        """计算非加权平均准确率

        每个类别的权重相同。

        Args:
            accuracy_dict_list: 准确率字典列表
            display_na_if_missing: 如果类别缺失是否显示 N/A

        Returns:
            包含 accuracy, total_count, display_accuracy 的字典
        """
        has_na = False
        total_count = 0
        total_accuracy = 0.0

        for accuracy_dict in accuracy_dict_list:
            accuracy = accuracy_dict["accuracy"]
            count = accuracy_dict["total_count"]
            if accuracy_dict.get("display_accuracy") == "N/A":
                has_na = True

            total_count += count
            total_accuracy += accuracy

        result = {
            "accuracy": total_accuracy / len(accuracy_dict_list) if accuracy_dict_list else 0.0,
            "total_count": total_count,
        }

        if has_na and display_na_if_missing:
            result["display_accuracy"] = "N/A"
        else:
            result["display_accuracy"] = result["accuracy"]

        return result

    def calculate_percentage_weighted_accuracy(
        self,
        accuracy_dict_list: List[Dict[str, Any]],
        weights: List[float],
        display_na_if_missing: bool = True,
    ) -> Dict[str, Any]:
        """计算百分比加权平均准确率

        使用固定的权重列表计算加权平均。

        Args:
            accuracy_dict_list: 准确率字典列表
            weights: 权重列表（会归一化）
            display_na_if_missing: 如果类别缺失是否显示 N/A

        Returns:
            包含 accuracy, total_count, display_accuracy 的字典
        """
        if len(accuracy_dict_list) != len(weights):
            raise ValueError("权重列表长度必须与准确率列表长度相同")

        has_na = False
        total_count = 0
        total_accuracy = 0.0
        weight_sum = sum(weights)

        if weight_sum == 0:
            raise ValueError("权重总和必须大于 0")

        # 归一化权重
        weights_norm = [w / weight_sum for w in weights]

        for accuracy_dict, weight in zip(accuracy_dict_list, weights_norm):
            accuracy = accuracy_dict["accuracy"]
            count = accuracy_dict["total_count"]
            if accuracy_dict.get("display_accuracy") == "N/A":
                has_na = True

            total_count += count
            total_accuracy += accuracy * weight

        result = {
            "accuracy": total_accuracy,
            "total_count": total_count,
        }

        if has_na and display_na_if_missing:
            result["display_accuracy"] = "N/A"
        else:
            result["display_accuracy"] = result["accuracy"]

        return result

    def get_category_score(self, category: str, default_total: int = 0) -> Dict[str, Any]:
        """获取指定类别的分数

        Args:
            category: 测试类别名称
            default_total: 如果类别不存在时的默认样本数

        Returns:
            包含 accuracy, total_count, display_accuracy 的字典
        """
        if category in self.category_results:
            score = self.category_results[category].copy()
            score["display_accuracy"] = score["accuracy"]
            return score
        else:
            return {
                "accuracy": 0.0,
                "total_count": default_total,
                "display_accuracy": "N/A",
            }

    def calculate_non_live_summary(self) -> Dict[str, Any]:
        """计算 Non-Live 类别的汇总分数

        Returns:
            包含各个 Non-Live 子类别和总体分数的字典
        """
        # 简单类别（Python, Java, JavaScript）
        python_simple = self.get_category_score("simple_python")
        java_simple = self.get_category_score("simple_java")
        javascript_simple = self.get_category_score("simple_javascript")

        simple_ast = self.calculate_unweighted_accuracy(
            [python_simple, java_simple, javascript_simple]
        )

        # 多函数类别
        multiple_ast = self.get_category_score("multiple")
        parallel_ast = self.get_category_score("parallel")
        parallel_multiple_ast = self.get_category_score("parallel_multiple")

        # AST 汇总
        summary_ast = self.calculate_unweighted_accuracy(
            [simple_ast, multiple_ast, parallel_ast, parallel_multiple_ast]
        )

        # 总体 Non-Live 分数
        overall_non_live = self.calculate_unweighted_accuracy(
            [simple_ast, multiple_ast, parallel_ast, parallel_multiple_ast],
            display_na_if_missing=False,
        )

        return {
            "simple_python": python_simple,
            "simple_java": java_simple,
            "simple_javascript": javascript_simple,
            "simple_ast": simple_ast,
            "multiple": multiple_ast,
            "parallel": parallel_ast,
            "parallel_multiple": parallel_multiple_ast,
            "summary_ast": summary_ast,
            "overall": overall_non_live,
            "irrelevance": self.get_category_score("irrelevance"),
        }

    def calculate_live_summary(self) -> Dict[str, Any]:
        """计算 Live 类别的汇总分数

        Returns:
            包含各个 Live 子类别和总体分数的字典
        """
        live_simple = self.get_category_score("live_simple")
        live_multiple = self.get_category_score("live_multiple")
        live_parallel = self.get_category_score("live_parallel")
        live_parallel_multiple = self.get_category_score("live_parallel_multiple")

        summary_ast = self.calculate_weighted_accuracy(
            [live_simple, live_multiple, live_parallel, live_parallel_multiple]
        )

        overall_live = self.calculate_weighted_accuracy(
            [live_simple, live_multiple, live_parallel, live_parallel_multiple],
            display_na_if_missing=False,
        )

        return {
            "live_simple": live_simple,
            "live_multiple": live_multiple,
            "live_parallel": live_parallel,
            "live_parallel_multiple": live_parallel_multiple,
            "summary_ast": summary_ast,
            "overall": overall_live,
            "irrelevance": self.get_category_score("live_irrelevance"),
            "relevance": self.get_category_score("live_relevance"),
        }

    def calculate_multi_turn_summary(self) -> Dict[str, Any]:
        """计算 Multi-Turn 类别的汇总分数

        Returns:
            包含各个 Multi-Turn 子类别和总体分数的字典
        """
        base = self.get_category_score("multi_turn_base")
        miss_func = self.get_category_score("multi_turn_miss_func")
        miss_param = self.get_category_score("multi_turn_miss_param")
        long_context = self.get_category_score("multi_turn_long_context")

        overall = self.calculate_unweighted_accuracy(
            [base, miss_func, miss_param, long_context],
            display_na_if_missing=False,
        )

        return {
            "base": base,
            "miss_func": miss_func,
            "miss_param": miss_param,
            "long_context": long_context,
            "overall": overall,
        }

    def calculate_agentic_summary(self) -> Dict[str, Any]:
        """计算 Agentic 类别的汇总分数

        Returns:
            包含各个 Agentic 子类别和总体分数的字典
        """
        # Web Search 子类别
        web_search_base = self.get_category_score("web_search_base")
        web_search_no_snippet = self.get_category_score("web_search_no_snippet")

        summary_web_search = self.calculate_unweighted_accuracy(
            [web_search_base, web_search_no_snippet]
        )

        # Memory 子类别
        memory_kv = self.get_category_score("memory_kv")
        memory_vector = self.get_category_score("memory_vector")
        memory_rec_sum = self.get_category_score("memory_rec_sum")

        summary_memory = self.calculate_unweighted_accuracy(
            [memory_kv, memory_vector, memory_rec_sum]
        )

        # 总体 Agentic 分数
        overall = self.calculate_unweighted_accuracy(
            [summary_web_search, summary_memory],
            display_na_if_missing=False,
        )

        return {
            "web_search_base": web_search_base,
            "web_search_no_snippet": web_search_no_snippet,
            "web_search_summary": summary_web_search,
            "memory_kv": memory_kv,
            "memory_vector": memory_vector,
            "memory_rec_sum": memory_rec_sum,
            "memory_summary": summary_memory,
            "overall": overall,
        }

    def calculate_overall_score(self) -> Dict[str, Any]:
        """计算总体分数

        Returns:
            包含所有类别和总体分数的字典
        """
        non_live_summary = self.calculate_non_live_summary()
        live_summary = self.calculate_live_summary()
        multi_turn_summary = self.calculate_multi_turn_summary()
        agentic_summary = self.calculate_agentic_summary()

        # 合并 irrelevance 分数
        total_irrelevance = self.calculate_unweighted_accuracy(
            [non_live_summary["irrelevance"], live_summary["irrelevance"]]
        )
        total_relevance = live_summary["relevance"]

        # 计算总体分数（使用百分比权重）
        overall_accuracy = self.calculate_percentage_weighted_accuracy(
            [
                non_live_summary["overall"],
                live_summary["overall"],
                total_irrelevance,
                multi_turn_summary["overall"],
                agentic_summary["overall"],
            ],
            list(self.OVERALL_WEIGHTS.values()),
            display_na_if_missing=False,
        )

        return {
            "non_live": non_live_summary,
            "live": live_summary,
            "multi_turn": multi_turn_summary,
            "agentic": agentic_summary,
            "irrelevance": total_irrelevance,
            "relevance": total_relevance,
            "overall": overall_accuracy,
        }

    def get_all_results(self) -> Dict[str, Any]:
        """获取所有聚合结果

        Returns:
            包含所有类别分数和总体分数的字典
        """
        return self.calculate_overall_score()
