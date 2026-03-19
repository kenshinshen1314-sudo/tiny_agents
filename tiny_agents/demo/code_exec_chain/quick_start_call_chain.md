# quick_start.py 完整调用链分析

> 文档生成时间: 2026-03-12
> 文件位置: `demo/agentic_rl/quick_start.py`

---

## 目录

- [整体架构](#整体架构)
- [调用链总览](#调用链总览)
- [测试1: 数据加载](#测试1-数据加载)
- [测试2: SFT训练](#测试2-sft训练)
- [测试3: GRPO训练](#测试3-grpo训练)
- [测试4: 奖励函数创建](#测试4-奖励函数创建)
- [模块依赖图](#模块依赖图)
- [关键数据流](#关键数据流)

---

## 整体架构

```
quick_start.py
    └── quick_test()
            ├── RLTrainingTool
            │   ├── 测试1: 数据加载 (_handle_load_dataset)
            │   ├── 测试2: SFT训练 (_train_sft)
            │   ├── 测试3: GRPO训练 (_train_grpo)
            │   └── 测试4: 奖励函数 (_handle_create_reward)
            └── 结果输出 (JSON格式)
```

---

## 调用链总览

### 主函数调用链

```
__main__
  └─> quick_test()
        ├─> RLTrainingTool()                    # 初始化工具
        │
        ├─> 测试1: tool.run(load_dataset)       # 数据加载测试
        ├─> 测试2: tool.run(train, sft)         # SFT训练测试
        ├─> 测试3: tool.run(train, grpo)        # GRPO训练测试
        └─> 测试4: tool.run(create_reward)      # 奖励函数测试
```

---

## 测试1: 数据加载

### 调用链路

```
quick_test()
  └─> tool.run({
        "action": "load_dataset",
        "format": "sft",
        "split": "train",
        "max_samples": 5
      })
      │
      └─> RLTrainingTool.run()
            └─> _handle_load_dataset(parameters)
                  │
                  ├─> tiny_agents.rl.create_sft_dataset()
                  │     │
                  │     └─> create_math_dataset()
                  │           │
                  │           └─> GSM8KDataset(format_type="sft")
                  │                 ├─> load_dataset("openai/gsm8k")
                  │                 ├─> dataset.select(range(max_samples))
                  │                 └─> dataset.map(format_for_sft)
                  │                       └─> 返回 {"prompt": ..., "completion": ...}
                  │
                  └─> 返回 JSON:
                        {
                          "status": "success",
                          "format": "sft",
                          "split": "train",
                          "dataset_size": 5,
                          "sample_keys": ["prompt", "completion"]
                        }
```

### 关键代码位置

| 模块 | 文件 | 行号 |
|------|------|------|
| `quick_test()` | `demo/agentic_rl/quick_start.py` | 18-154 |
| `RLTrainingTool.run()` | `tools/builtin/rl_training_tool.py` | 71-139 |
| `_handle_load_dataset()` | `tools/builtin/rl_training_tool.py` | 224-250 |
| `create_sft_dataset()` | `rl/datasets.py` | 284-303 |
| `GSM8KDataset` | `rl/datasets.py` | 9-157 |

### 数据格式

```python
# SFT格式输出
{
    "prompt": "Question: {问题}\n\nLet's solve this step by step:\n",
    "completion": "{推理过程}\n\nFinal Answer: {最终答案}",
    "text": "{prompt}{completion}"  # 完整文本
}
```

---

## 测试2: SFT训练

### 调用链路

```
quick_test()
  └─> tool.run({
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/quick_test/sft",
        "max_samples": 10,
        "num_epochs": 1,
        "batch_size": 2,
        "use_lora": True,
        "lora_r": 8,
        "lora_alpha": 16,
      })
      │
      └─> RLTrainingTool.run()
            └─> _handle_train(parameters)
                  └─> _train_sft(...)
                        │
                        ├─> TrainingConfig(...)                   # 创建配置
                        ├─> setup_training_environment(config)     # 设置环境
                        ├─> create_sft_dataset(max_samples)       # 加载数据
                        ├─> SFTTrainerWrapper(config, dataset)
                        │     │
                        │     ├─> setup_model()
                        │     │     ├─> AutoTokenizer.from_pretrained()
                        │     │     └─> AutoModelForCausalLM.from_pretrained()
                        │     │
                        │     ├─> SFTConfig(...)                   # TRL配置
                        │     ├─> DetailedLoggingCallback(...)      # 日志回调
                        │     ├─> SFTTrainer(...)                  # TRL训练器
                        │     └─> trainer.train()                  # 执行训练
                        │           └─> [trl内部训练循环]
                        │
                        └─> trainer_wrapper.save_model()          # 保存模型
                              └─> 返回 JSON 结果
```

### SFT训练器内部流程

```
SFTTrainerWrapper.train()
  │
  ├─> SFTConfig 配置参数
  │     ├─ output_dir: "./output/quick_test/sft"
  │     ├─ num_train_epochs: 1
  │     ├─ per_device_train_batch_size: 2
  │     ├─ learning_rate: 5e-5
  │     ├─ logging_steps: 10
  │     ├─ fp16: True
  │     └─ report_to: ["tensorboard"]
  │
  ├─> 创建 SFTTrainer (trl库)
  │     ├─ model: Qwen/Qwen3-0.6B
  │     ├─ args: SFTConfig
  │     ├─ train_dataset: GSM8K (10样本)
  │     ├─ processing_class: tokenizer
  │     └─ callbacks: [DetailedLoggingCallback]
  │
  ├─> trainer.train() 执行训练
  │     │
  │     ├─> 每个batch:
  │     │     ├─ tokenize输入
  │     │     ├─ forward pass
  │     │     ├─ compute loss
  │     │     ├─ backward pass
  │     │     └─ optimizer step
  │     │
  │     └─> logging_callback.on_log()
  │           └─> 打印: Epoch | Step | Loss | LR
  │
  └─> 保存模型到 output_dir
```

### 关键代码位置

| 模块 | 文件 | 行号 |
|------|------|------|
| `_train_sft()` | `tools/builtin/rl_training_tool.py` | 418-484 |
| `SFTTrainerWrapper` | `rl/trainers.py` | 132-240 |
| `TrainingConfig` | `rl/utils.py` | 9-60 |
| `setup_training_environment()` | `rl/utils.py` | 62-99 |
| `SFTConfig` | [trl库] | - |

---

## 测试3: GRPO训练

### 调用链路

```
quick_test()
  └─> tool.run({
        "action": "train",
        "algorithm": "grpo",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/quick_test/grpo",
        "max_samples": 10,
        "num_epochs": 1,
        "batch_size": 2,
        "use_lora": True,
        "lora_r": 8,
        "lora_alpha": 16,
      })
      │
      └─> RLTrainingTool.run()
            └─> _handle_train(parameters)
                  └─> _train_grpo(...)
                        │
                        ├─> TrainingConfig(...)                   # 创建配置
                        ├─> setup_training_environment(config)     # 设置环境
                        ├─> create_rl_dataset(max_samples, model)  # 加载RL数据
                        │     └─> create_math_dataset(format_type="rl")
                        │           └─> GSM8KDataset(format_type="rl")
                        │                 └─> format_for_rl()
                        │                       └─> 应用chat template
                        │
                        ├─> create_accuracy_reward()              # 创建奖励函数
                        │     └─> MathRewardFunction()
                        │
                        ├─> GRPOTrainerWrapper(config, dataset, reward_fn)
                        │     │
                        │     ├─> setup_model()
                        │     │     ├─> AutoTokenizer.from_pretrained()
                        │     │     └─> AutoModelForCausalLM.from_pretrained()
                        │     │
                        │     ├─> GRPOConfig(...)                  # TRL配置
                        │     ├─> DetailedLoggingCallback(...)      # 日志回调
                        │     ├─> GRPOTrainer(...)                 # TRL训练器
                        │     └─> trainer.train()                  # 执行训练
                        │           └─> [trl内部GRPO循环]
                        │
                        └─> trainer_wrapper.save_model()          # 保存模型
                              └─> 返回 JSON 结果
```

### GRPO训练器内部流程

```
GRPOTrainerWrapper.train()
  │
  ├─> GRPOConfig 配置参数
  │     ├─ output_dir: "./output/quick_test/grpo"
  │     ├─ num_train_epochs: 1
  │     ├─ per_device_train_batch_size: 2
  │     ├─ learning_rate: 1e-5
  │     ├─ remove_unused_columns: False
  │     └─ report_to: ["tensorboard"]
  │
  ├─> 创建 GRPOTrainer (trl库)
  │     ├─ model: Qwen/Qwen3-0.6B
  │     ├─ args: GRPOConfig
  │     ├─ train_dataset: GSM8K (RL格式)
  │     ├─ reward_funcs: MathRewardFunction
  │     ├─ processing_class: tokenizer
  │     └─ callbacks: [DetailedLoggingCallback]
  │
  ├─> trainer.train() 执行GRPO训练
  │     │
  │     ├─> 生成阶段:
  │     │     ├─ 生成completion (采样生成)
  │     │     └─ 获取多个候选答案
  │     │
  │     ├─> 奖励计算:
  │     │     ├─ reward_fn(completions, ground_truth)
  │     │     └─ MathRewardFunction.__call__()
  │     │           ├─> extract_answer()   # 提取答案
  │     │           ├─> normalize_answer() # 标准化
  │     │           └─> compare_answers()  # 比较
  │     │
  │     ├─> 优势计算:
  │     │     └─> 计算相对优势
  │     │
  │     ├─> 策略更新:
  │     │     ├─ compute GRPO loss
  │     │     ├─ backward pass
  │     │     └─ optimizer step
  │     │
  │     └─> logging_callback.on_log()
  │           └─> 打印: Epoch | Step | Reward | KL
  │
  └─> 保存模型到 output_dir
```

### 关键代码位置

| 模块 | 文件 | 行号 |
|------|------|------|
| `_train_grpo()` | `tools/builtin/rl_training_tool.py` | 486-571 |
| `GRPOTrainerWrapper` | `rl/trainers.py` | 242-357 |
| `create_rl_dataset()` | `rl/datasets.py` | 306-332 |
| `create_accuracy_reward()` | `rl/rewards.py` | 142-153 |
| `MathRewardFunction` | `rl/rewards.py` | 7-139 |

---

## 测试4: 奖励函数创建

### 调用链路

```
quick_test()
  └─> tool.run({
        "action": "create_reward",
        "reward_type": "accuracy"
      })
      │
      └─> RLTrainingTool.run()
            └─> _handle_create_reward(parameters)
                  │
                  └─> create_accuracy_reward()
                        │
                        └─> MathRewardFunction(tolerance=1e-4)
                              ├─> __init__()
                              ├─> extract_answer()
                              ├─> normalize_answer()
                              └─> compare_answers()
                              └─> 返回 JSON 结果
```

### 奖励函数详解

```
MathRewardFunction.__call__(completions, **kwargs)
  │
  ├─> 获取 ground_truth
  │     └─> ground_truths = kwargs.get("ground_truth", [])
  │
  ├─> 遍历每个completion和ground_truth
  │     │
  │     ├─> 提取预测答案
  │     │     └─> extract_answer(completion)
  │     │           ├─> 匹配 "Final Answer: {answer}"
  │     │           ├─> 匹配 "#### {answer}"
  │     │           ├─> 匹配 "答案是: {answer}"
  │     │           └─> 提取最后一行的数字
  │     │
  │     ├─> 标准化答案
  │     │     └─> normalize_answer()
  │     │           ├─> 移除符号: , $ %
  │     │           ├─> 提取数字: r'-?\d+\.?\d*'
  │     │           └─> 转换为 float
  │     │
  │     ├─> 比较答案
  │     │     └─> compare_answers(pred, truth)
  │     │           ├─> 数值比较: abs(pred - truth) < tolerance
  │     │           └─> 字符串比较: pred.lower() == truth.lower()
  │     │
  │     └─> 计算奖励
  │           └─> reward = 1.0 (正确) 或 0.0 (错误)
  │
  └─> 返回 rewards列表
```

### 关键代码位置

| 模块 | 文件 | 行号 |
|------|------|------|
| `_handle_create_reward()` | `tools/builtin/rl_training_tool.py` | 252-306 |
| `create_accuracy_reward()` | `rl/rewards.py` | 142-153 |
| `MathRewardFunction` | `rl/rewards.py` | 7-139 |

---

## 模块依赖图

```
quick_start.py
    │
    ├─> tiny_agents.tools
    │     └─> RLTrainingTool
    │           ├─> tiny_agents.rl.trainers
    │           │     ├─> SFTTrainerWrapper
    │           │     ├─> GRPOTrainerWrapper
    │           │     └─> PPOTrainerWrapper
    │           │
    │           ├─> tiny_agents.rl.datasets
    │           │     ├─> GSM8KDataset
    │           │     ├─> create_sft_dataset
    │           │     ├─> create_rl_dataset
    │           │     └─> create_math_dataset
    │           │
    │           ├─> tiny_agents.rl.rewards
    │           │     ├─> MathRewardFunction
    │           │     ├─> create_accuracy_reward
    │           │     ├─> create_length_penalty_reward
    │           │     └─> create_step_reward
    │           │
    │           └─> tiny_agents.rl.utils
    │                 ├─> TrainingConfig
    │                 └─> setup_training_environment
    │
    └─> 外部依赖
          ├─> trl (HuggingFace TRL库)
          │     ├─> SFTTrainer
          │     ├─> GRPOTrainer
          │     ├─> SFTConfig
          │     └─> GRPOConfig
          │
          ├─> transformers
          │     ├─> AutoModelForCausalLM
          │     ├─> AutoTokenizer
          │     └─> TrainerCallback
          │
          └─> datasets
                └─> load_dataset
```

---

## 关键数据流

### 数据集格式转换流程

```
原始GSM8K数据
    {
        "question": "Natalia sold clips...",
        "answer": "Natalia sold 48 clips...\n#### 48"
    }
         │
         ▼ format_for_sft()
SFT格式数据
    {
        "prompt": "Question: Natalia sold clips...\n\nLet's solve this step by step:\n",
        "completion": "Natalia sold 48 clips...\n\nFinal Answer: 48",
        "text": "Question:...\n\nLet's solve this step by step:\nNatalia sold 48 clips...\n\nFinal Answer: 48"
    }
         │
         ▼ format_for_rl()
RL格式数据
    {
        "prompt": "<|im_start|>user\nQuestion: Natalia sold clips...\n\nLet's solve this step by step:<|im_end|>\n<|im_start|>assistant\n",
        "ground_truth": "48",
        "question": "Natalia sold clips...",
        "full_answer": "Natalia sold 48 clips...\n#### 48"
    }
```

### 训练配置参数流

```
quick_start.py配置
    {
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/quick_test/sft",
        "max_samples": 10,
        "num_epochs": 1,
        "batch_size": 2,
        "use_lora": True,
        "lora_r": 8,
        "lora_alpha": 16,
    }
         │
         ▼ _train_sft()
TrainingConfig
    {
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/quick_test/sft",
        "num_train_epochs": 1,
        "per_device_train_batch_size": 2,
        "learning_rate": 5e-5,
        "use_lora": True,
        "lora_r": 8,
        "lora_alpha": 16,
        "use_fp16": True,
        "use_tensorboard": True,
        ...
    }
         │
         ▼ SFTConfig()
TRL SFTConfig
    {
        "output_dir": "./output/quick_test/sft",
        "num_train_epochs": 1,
        "per_device_train_batch_size": 2,
        "learning_rate": 5e-5,
        "fp16": True,
        "max_length": 2048,
        "report_to": ["tensorboard"],
        ...
    }
```

---

## 时间线总结

```
┌─────────────────────────────────────────────────────────────────┐
│ quick_test() 执行流程                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 1: 初始化                                                │
│  ├─ 创建 RLTrainingTool                                         │
│  └─ 检查 TRL 可用性                                             │
│                                                                  │
│  Phase 2: 数据加载测试 (~5秒)                                    │
│  ├─ 加载 GSM8K 数据集 (5样本)                                    │
│  ├─ 格式化为 SFT 格式                                            │
│  └─ 返回数据集信息                                               │
│                                                                  │
│  Phase 3: SFT训练 (~1-2分钟)                                    │
│  ├─ 设置训练环境                                                 │
│  ├─ 加载 Qwen/Qwen3-0.6B 模型                                   │
│  ├─ 加载 tokenizer                                               │
│  ├─ 创建 SFTTrainer                                             │
│  ├─ 训练 1 epoch, 10 样本                                        │
│  └─ 保存模型到 ./output/quick_test/sft                          │
│                                                                  │
│  Phase 4: GRPO训练 (~1-2分钟)                                   │
│  ├─ 加载 Qwen/Qwen3-0.6B 模型                                   │
│  ├─ 加载 RL 格式数据集 (10样本)                                  │
│  ├─ 创建准确性奖励函数                                           │
│  ├─ 创建 GRPOTrainer                                            │
│  ├─ 训练 1 epoch, 10 样本                                        │
│  └─ 保存模型到 ./output/quick_test/grpo                         │
│                                                                  │
│  Phase 5: 奖励函数测试 (<1秒)                                    │
│  ├─ 创建 MathRewardFunction                                     │
│  └─ 返回奖励函数信息                                             │
│                                                                  │
│  Phase 6: 总结                                                   │
│  └─ 输出所有测试结果                                             │
│                                                                  │
│  预计总时间: 2-3分钟 (CPU) / 30-60秒 (GPU)                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 附录: 快速参考

### 文件路径速查

| 组件 | 路径 |
|------|------|
| 主脚本 | `demo/agentic_rl/quick_start.py` |
| RL工具 | `tools/builtin/rl_training_tool.py` |
| 训练器 | `rl/trainers.py` |
| 数据集 | `rl/datasets.py` |
| 奖励函数 | `rl/rewards.py` |
| 工具函数 | `rl/utils.py` |

### 配置默认值

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `model_name` | `Qwen/Qwen3-0.6B` | 基础模型 |
| `max_samples` | 10 | 快速测试样本数 |
| `num_epochs` | 1 | 训练轮数 |
| `batch_size` | 2 | 批次大小 |
| `use_lora` | True | 使用LoRA |
| `lora_r` | 8 | LoRA秩 |
| `lora_alpha` | 16 | LoRA alpha |

### 输出目录结构

```
output/quick_test/
├── sft/                    # SFT训练输出
│   ├── checkpoint-*/        # 检查点
│   ├── adapter_config.json  # LoRA配置
│   └── adapter_model.safetensors  # LoRA权重
│
└── grpo/                   # GRPO训练输出
    ├── checkpoint-*/        # 检查点
    ├── adapter_config.json  # LoRA配置
    ├── adapter_model.safetensors  # LoRA权重
    └── runs/                # TensorBoard日志
        └── events.out.tfevents.*
```

---

> **文档版本**: v1.0
> **最后更新**: 2026-03-12
> **作者**: Tiny Agents Team
