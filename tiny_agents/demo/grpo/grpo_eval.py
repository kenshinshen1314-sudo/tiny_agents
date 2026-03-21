import json

from tiny_agents.tools import RLTrainingTool

rl_tool = RLTrainingTool()

# 全面评估
print("=" * 50)
print("全面评估GRPO模型")
print("=" * 50)

result = rl_tool.run({
    "action": "evaluate",
    "model_path": "./models/grpo_model",
    "max_samples": 200,
    "use_lora": True,
    
    # 评估配置
    "metrics": [
        "accuracy",           # 准确率
        "accuracy_at_k",      # Top-K准确率
        "average_length",     # 平均长度
        "average_steps",      # 平均步骤数
        "format_correctness", # 格式正确率
    ],
    "k": 3,  # Top-3准确率
})

# 解析结果
eval_data = json.loads(result)

# 打印结果
print(f"\n评估结果:")
print(f"  准确率: {eval_data['accuracy']}")
print(f"  平均奖励: {eval_data['average_reward']}")
print(f"  测试样本数: {eval_data['num_samples']}")
