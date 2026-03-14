from datasets import Dataset
from tiny_agents.rl import format_math_dataset
from tiny_agents.tools import RLTrainingTool
from typing import List

import re

# 1. 准备自定义数据
custom_data = [
    {"question": "What is 2+2?", "answer": "2+2=4. #### 4"},
    {"question": "What is 5+3?", "answer": "5+3=8. #### 8"},
    {"question": "What is 10+7?", "answer": "10+7=17. #### 17"}
]

# 2. 转换为数据集
raw_dataset = Dataset.from_list(custom_data)
rl_dataset = format_math_dataset(raw_dataset, format_type="rl")

# 3. 定义奖励函数
def tolerant_reward_fn(completions: List[str], **kwargs) -> List[float]:
    """
    容忍奖励函数，允许答案有微小的误差
    """
    ground_truth = kwargs.get("ground_truth", [])
    rewards = []

    for completion, truth in zip(completions, ground_truth):
        # 提取答案中的数字
        numbers = re.search(r"-?\d+\.?\d*", completion)
        if numbers:
            try:
                pred_val = float(numbers[-1])
                truth_val = float(truth)
                error = abs(pred_val - truth_val)

                if error <= 0.01:
                    reward = 1.0
                elif error <= 5:
                    reward = 0.5
                else:
                    reward = 0.0
            except ValueError:
                reward = 0.0  # 转换失败，奖励为0
        else:
            reward = 0.0  # 没有提取到数字，奖励为0

        rewards.append(reward)
    
    return rewards

# 4. 
rl_tool = RLTrainingTool()
rl_tool.register_dataset("my_dataset", rl_dataset)
rl_tool.register_reward_function("tolerant_reward_fn", tolerant_reward_fn)

params_dict = {
    "action_type": "train",
    "algorithm": "grpo",
    "model_name": "Qwen/Qwen3-0.6B",
    "dataset": "my_dataset",
    "output_dir": "./models/custom_grpo",
    "num_epochs": 2,
    "batch_size": 2,
    "learning_rate": 1e-5
}

# 5. 开始训练
result =rl_tool.run(
    parameters=params_dict
)