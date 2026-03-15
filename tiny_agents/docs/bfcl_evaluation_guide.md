# BFCL 评估流程使用指南

## 概述

BFCL (Berkeley Function Calling Leaderboard) 评估流程是一个完整的工具调用能力评估系统，支持：

- ✅ 多类别评估（Non-Live、Live、Multi-Turn、Agentic）
- ✅ 部分评估支持（partial_eval）
- ✅ 数据聚合和指标计算
- ✅ CSV 格式导出（符合 BFCL 官方规范）
- ✅ 官方评估工具集成
- ✅ 详细评估报告生成

## 快速开始

### 基本使用

```python
from tiny_agents import SimpleAgent
from tiny_agents.tools.builtin import BFCLEvaluationToolV2

# 创建智能体
agent = SimpleAgent(name="MyAgent")

# 创建评估工具
bfcl_tool = BFCLEvaluationToolV2()

# 运行评估
results = bfcl_tool.run(
    agent=agent,
    test_categories=["simple_python"],
    max_samples=5,
    model_name="MyModel",
    partial_eval=True,
)

print(f"准确率: {results['overall_accuracy']:.2%}")
```

### 完整评估

```python
results = bfcl_tool.run(
    agent=agent,
    test_categories=["all_scoring"],  # 评估所有计分类别
    max_samples=0,  # 评估全部样本
    model_name="MyModel",
    partial_eval=False,  # 要求所有类别都有结果
    run_official_eval=True,  # 运行官方评估
    export_csv=True,  # 导出 CSV
    generate_report=True,  # 生成报告
)
```

## 评估类别

### Non-Live 类别

非实时测试类别，评估静态函数调用能力：

| 类别 | 描述 |
|------|------|
| `simple_python` | 简单 Python 函数调用 |
| `simple_java` | 简单 Java 函数调用 |
| `simple_javascript` | 简单 JavaScript 函数调用 |
| `multiple` | 多函数调用 |
| `parallel` | 并行函数调用 |
| `parallel_multiple` | 并行多函数调用 |
| `irrelevance` | 无关检测（不应调用函数） |

### Live 类别

实时测试类别，评估动态 API 调用能力：

| 类别 | 描述 |
|------|------|
| `live_simple` | 实时简单函数调用 |
| `live_multiple` | 实时多函数调用 |
| `live_parallel` | 实时并行函数调用 |
| `live_parallel_multiple` | 实时并行多函数调用 |
| `live_irrelevance` | 实时无关检测 |
| `live_relevance` | 实时相关检测 |

### Multi-Turn 类别

多轮对话测试类别，评估复杂交互能力：

| 类别 | 描述 |
|------|------|
| `multi_turn_base` | 基础多轮对话 |
| `multi_turn_miss_func` | 缺失函数的多轮对话 |
| `multi_turn_miss_param` | 缺失参数的多轮对话 |
| `multi_turn_long_context` | 长上下文多轮对话 |

### Agentic 类别

智能体测试类别，评估高级智能体能力：

| 类别 | 描述 |
|------|------|
| `memory_kv` | KV 存储能力 |
| `memory_vector` | 向量存储能力 |
| `memory_rec_sum` | 递归摘要能力 |
| `web_search_base` | 基础网页搜索 |
| `web_search_no_snippet` | 无摘要网页搜索 |

### 组合类别

| 类别 | 描述 |
|------|------|
| `all` | 所有类别 |
| `all_scoring` | 所有计分类别 |
| `non_live` | 所有 Non-Live 类别 |
| `live` | 所有 Live 类别 |
| `multi_turn` | 所有 Multi-Turn 类别 |
| `agentic` | 所有 Agentic 类别 |

## 数据聚合机制

### 权重分配

总体指标使用百分比加权平均计算：

| 指标 | 权重 | 说明 |
|------|------|------|
| Non-Live | 10% | 静态函数调用 |
| Live | 10% | 动态 API 调用 |
| Irrelevance | 10% | 无关检测 |
| Multi-Turn | 30% | 多轮对话 |
| Agentic | 40% | 智能体能力 |

### 聚合方法

- **加权平均**: 用于 Non-Live 和 Live 类别（权重 = 样本数）
- **非加权平均**: 用于 Multi-Turn 和 Agentic 类别（每个子类别权重相同）
- **百分比加权平均**: 用于总体指标（使用固定权重）

## CSV 输出格式

### 文件列表

| 文件名 | 描述 |
|--------|------|
| `data_overall.csv` | 主排行榜，综合所有指标 |
| `data_live.csv` | Live 测试类别详细结果 |
| `data_non_live.csv` | Non-Live 测试类别详细结果 |
| `data_multi_turn.csv` | Multi-Turn 类别详细结果 |
| `data_agentic.csv` | Agentic 类别详细结果 |

### data_overall.csv 列

```
Rank, Overall Acc, Model, Link, Cost, Latency, Std, 95th Percentile,
Non-Live AST Acc, Non-Live Simple Acc, Non-Live Multiple Acc,
Non-Live Parallel Acc, Non-Live Parallel Multiple Acc,
Live Acc, Live Simple Acc, Live Multiple Acc,
Live Parallel Acc, Live Parallel Multiple Acc,
Multi Turn Acc, Multi Turn Base Acc, Multi Turn Miss Func Acc,
Multi Turn Miss Param Acc, Multi Turn Long Context Acc,
Web Search Acc, Web Search Base Acc, Web Search No Snippet Acc,
Memory Acc, Memory KV Acc, Memory Vector Acc, Memory Rec Sum Acc,
Relevance, Irrelevance,
Format Sensitivity Max Delta, Format Sensitivity Std,
Organization, License
```

## partial_eval 标志

### 作用

`partial_eval` 标志控制评估行为：

| 值 | 行为 |
|---|------|
| `False` (默认) | 要求模型结果包含所有测试条目，否则抛出异常 |
| `True` | 只评估模型结果中存在的条目，忽略缺失的 ID |

### 使用场景

**partial_eval=True** (推荐用于开发测试):
- 快速测试单个类别
- 部分样本评估
- 调试和开发

**partial_eval=False** (用于正式评估):
- 完整评估
- 生成官方可比较的结果
- 确保数据完整性

## 官方评估集成

### 安装 BFCL 官方工具

```bash
pip install bfcl-eval
```

### 运行官方评估

```python
results = bfcl_tool.run(
    agent=agent,
    test_categories=["simple_python"],
    run_official_eval=True,  # 启用官方评估
    model_name="Qwen/Qwen3-8B",
)
```

### 官方评估输出

官方评估结果保存在 `score/` 目录：

```
score/
├── data_overall.csv           # 主排行榜
├── data_live.csv              # Live 详细结果
├── data_non_live.csv          # Non-Live 详细结果
├── data_multi_turn.csv        # Multi-Turn 详细结果
├── data_agentic.csv           # Agentic 详细结果
└── Qwen_Qwen3-8B/            # 模型评分详情
    └── non_live/
        └── BFCL_v4_simple_python_score.json
```

## 评估报告

### 报告内容

评估报告包含：

1. **评估概览**: 智能体名称、评估类别、总体准确率
2. **详细指标**: 每个子类别的准确率和样本数
3. **总体指标**: 按权重汇总的总体分数
4. **生成的文件**: CSV 文件路径
5. **建议**: 基于表现的改进建议

### 报告示例

```markdown
# BFCL 评估报告

**生成时间**: 2024-01-01 12:00:00

## 📊 评估概览

- **智能体**: MyAgent
- **评估类别**: simple_python
- **总体准确率**: 85.50%

## 📈 详细指标

### Non-Live 测试

| 类别 | 准确率 | 正确数/总数 |
|------|--------|-------------|
| Python Simple | 85.50% | 342/400 |

## 🎯 总体指标

| 指标 | 权重 | 分数 |
|------|------|------|
| Non-Live | 10% | 85.50% |
| **Overall** | 100% | 85.50% |

## 💡 建议

- ⚠️ 表现良好，但仍有提升空间。建议检查错误样本。
```

## 高级功能

### 自定义聚合器

```python
from tiny_agents.evaluation.benchmarks.bfcl.aggregation import (
    BFCLEvaluationAggregator,
)

# 创建聚合器
aggregator = BFCLEvaluationAggregator()

# 添加类别结果
aggregator.add_category_result(
    category="simple_python",
    accuracy=0.855,
    correct_count=342,
    total_count=400,
)

# 计算总体分数
overall = aggregator.get_all_results()
```

### 自定义 CSV 导出

```python
from tiny_agents.evaluation.benchmarks.bfcl.csv_exporter import (
    BFCLEvaluationCSVExporter,
)

# 创建导出器
exporter = BFCLEvaluationCSVExporter(output_dir="my_output")

# 导出 CSV
csv_paths = exporter.export([{
    "model_name": "MyModel",
    "model_url": "https://example.com",
    "aggregated_results": aggregated_results,
}])
```

## 常见问题

### Q: 如何只评估特定类别？

A: 使用 `test_categories` 参数：

```python
results = bfcl_tool.run(
    agent=agent,
    test_categories=["simple_python", "simple_java"],
)
```

### Q: 如何限制每个类别的样本数？

A: 使用 `max_samples` 参数：

```python
results = bfcl_tool.run(
    agent=agent,
    test_categories=["simple_python"],
    max_samples=10,  # 只评估 10 个样本
)
```

### Q: partial_eval 和 max_samples 的区别？

A:
- `partial_eval`: 控制是否要求所有测试条目都有结果
- `max_samples`: 控制每个类别评估的最大样本数

### Q: 如何与官方 BFCL 排行榜比较？

A: 使用 `run_official_eval=True` 并确保评估全部样本：

```python
results = bfcl_tool.run(
    agent=agent,
    test_categories=["all_scoring"],
    max_samples=0,  # 评估全部样本
    partial_eval=False,  # 要求完整结果
    run_official_eval=True,
)
```

## 参考资源

- [BFCL 官网](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [BFCL 数据集](https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard)
- [BFCL GitHub](https://github.com/ShishirPatil/gorilla)
