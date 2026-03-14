"""RL训练器封装

本模块封装了TRL的各种训练器，提供统一的接口。
"""

from typing import Optional, Callable, Dict, Any
from pathlib import Path

from .utils import TrainingConfig, check_trl_installation, get_installation_guide

try:
    from transformers import TrainerCallback

    class DetailedLoggingCallback(TrainerCallback):
        """详细日志回调

        在训练过程中输出更详细的日志信息,包括:
        - Epoch/Step进度
        - Loss
        - Learning Rate
        - Reward (GRPO)
        - KL散度 (GRPO)
        """

        def __init__(self, total_steps: int = None, num_epochs: int = None):
            """
            初始化回调

            Args:
                total_steps: 总步数
                num_epochs: 总轮数
            """
            self.total_steps = total_steps
            self.num_epochs = num_epochs
            self.current_epoch = 0

        def on_log(self, args, state, control, logs=None, **kwargs):
            """日志回调"""
            if logs is None:
                return

            # 计算当前epoch
            if state.epoch is not None:
                self.current_epoch = int(state.epoch)

            # 构建日志消息
            log_parts = []

            # Epoch和Step信息
            if self.num_epochs:
                log_parts.append(f"Epoch {self.current_epoch + 1}/{self.num_epochs}")

            if state.global_step and self.total_steps:
                log_parts.append(f"Step {state.global_step}/{self.total_steps}")
            elif state.global_step:
                log_parts.append(f"Step {state.global_step}")

            # Loss
            if "loss" in logs:
                log_parts.append(f"Loss: {logs['loss']:.4f}")

            # Learning Rate
            if "learning_rate" in logs:
                log_parts.append(f"LR: {logs['learning_rate']:.2e}")

            # GRPO特定指标
            if "rewards/mean" in logs:
                log_parts.append(f"Reward: {logs['rewards/mean']:.4f}")

            if "objective/kl" in logs:
                log_parts.append(f"KL: {logs['objective/kl']:.4f}")

            # 输出日志
            if log_parts:
                print(" | ".join(log_parts))

        def on_epoch_end(self, args, state, control, **kwargs):
            """Epoch结束回调"""
            print(f"{'='*80}")
            print(f"✅ Epoch {self.current_epoch + 1} 完成")
            print(f"{'='*80}\n")

except ImportError:
    # 如果transformers未安装,创建一个空的回调类
    class DetailedLoggingCallback:
        def __init__(self, *args, **kwargs):
            pass


class BaseTrainerWrapper:
    """训练器基类"""
    
    def __init__(self, config: Optional[TrainingConfig] = None):
        """
        初始化训练器
        
        Args:
            config: 训练配置
        """
        # 检查TRL是否安装
        if not check_trl_installation():
            raise ImportError(get_installation_guide())
        
        self.config = config or TrainingConfig()
        self.trainer = None
        self.model = None
        self.tokenizer = None
    
    def setup_model(self):
        """设置模型和tokenizer"""
        raise NotImplementedError
    
    def train(self):
        """开始训练"""
        raise NotImplementedError
    
    def save_model(self, output_dir: Optional[str] = None):
        """
        保存模型
        
        Args:
            output_dir: 输出目录
        """
        save_dir = output_dir or self.config.output_dir
        if self.trainer:
            self.trainer.save_model(save_dir)
            print(f"✅ 模型已保存到: {save_dir}")
        else:
            print("❌ 训练器未初始化，无法保存模型")


class SFTTrainerWrapper(BaseTrainerWrapper):
    """SFT (Supervised Fine-Tuning) 训练器封装
    
    用于监督微调，让模型学会遵循指令和基本的推理格式。
    """
    
    def __init__(
        self,
        config: Optional[TrainingConfig] = None,
        dataset = None
    ):
        """
        初始化SFT训练器
        
        Args:
            config: 训练配置
            dataset: 训练数据集
        """
        super().__init__(config)
        self.dataset = dataset
    
    def setup_model(self):
        """设置模型和tokenizer"""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        print(f"📦 加载模型: {self.config.model_name}")
        
        # 加载tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # 加载模型
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            trust_remote_code=True,
            device_map="auto" if self.config.use_fp16 or self.config.use_bf16 else None
        )
        
        print("✅ 模型加载完成")
    
    def train(self):
        """开始SFT训练"""
        from trl import SFTConfig, SFTTrainer
        import torch

        if self.model is None:
            self.setup_model()

        if self.dataset is None:
            raise ValueError("数据集未设置，请提供训练数据集")

        # 🔍 诊断：检测设备类型
        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"

        print(f"\n{'='*80}")
        print(f"🔍 诊断信息:")
        print(f"   设备类型: {device}")
        print(f"   数据集大小: {len(self.dataset)}")
        print(f"   训练轮数: {self.config.num_train_epochs}")
        print(f"   批次大小: {self.config.per_device_train_batch_size}")
        print(f"   梯度累积步数: {self.config.gradient_accumulation_steps}")
        print(f"{'='*80}\n")

        # 配置训练参数
        # 确定report_to参数
        report_to = []
        if self.config.use_wandb:
            report_to.append("wandb")
        if self.config.use_tensorboard:
            report_to.append("tensorboard")
        if not report_to:
            report_to = ["none"]

        # 🔍 修复：MPS 设备需要禁用 pin_memory
        # 修复 MPS 警告: 'pin_memory' argument is set as true but not supported on MPS
        dataloader_pin_memory = device != "mps"

        training_args = SFTConfig(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            fp16=self.config.use_fp16 and device == "cuda",  # fp16 仅在 CUDA 上启用
            bf16=self.config.use_bf16 and device == "cuda",  # bf16 仅在 CUDA 上启用
            gradient_checkpointing=self.config.gradient_checkpointing,
            max_length=self.config.max_length,
            report_to=report_to,
            dataloader_pin_memory=dataloader_pin_memory,  # 修复 MPS 兼容性
        )

        # 🔍 诊断：打印完整配置
        print(f"📋 SFTConfig 配置:")
        for key, value in sorted(training_args.__dict__.items()):
            if not key.startswith('_'):
                print(f"   {key}: {value}")

        # 检查 max_steps 默认值（可能导致训练提前结束）
        max_steps = training_args.__dict__.get('max_steps', -1)
        if max_steps > 0 and max_steps < 1000:
            print(f"\n⚠️  警告: max_steps={max_steps} 可能导致训练提前结束!")
            print(f"   建议设置 max_steps=-1 (无限制) 或更大的值")

        # 计算总步数
        total_steps = (
            len(self.dataset) //
            (self.config.per_device_train_batch_size * self.config.gradient_accumulation_steps)
        ) * self.config.num_train_epochs

        print(f"\n📊 预期训练步数: {total_steps}")
        print(f"   (数据集大小 {len(self.dataset)} / 批次大小 {self.config.per_device_train_batch_size} / 梯度累积 {self.config.gradient_accumulation_steps} × 轮数 {self.config.num_train_epochs})")
        print(f"{'='*80}\n")

        # 创建详细日志回调
        logging_callback = DetailedLoggingCallback(
            total_steps=total_steps,
            num_epochs=self.config.num_train_epochs
        )

        # 创建训练器
        self.trainer = SFTTrainer(
            model=self.model,
            args=training_args,
            train_dataset=self.dataset,
            processing_class=self.tokenizer,
            callbacks=[logging_callback],
        )

        # 🔍 诊断：打印 trainer 初始状态
        print(f"🔧 Trainer 初始化完成:")
        print(f"   总步数: {self.trainer.args.max_steps if hasattr(self.trainer.args, 'max_steps') else '使用 epochs 计算'}")
        print(f"   优化器步数: {getattr(self.trainer.state, 'max_steps', '未知')}")
        print(f"{'='*80}\n")

        print("\n🚀 开始SFT训练...")
        print(f"{'='*80}\n")

        # 🔍 诊断：使用 try-catch 捕获训练异常
        try:
            result = self.trainer.train()

            # 检查训练是否真的完成
            actual_steps = result.global_step if hasattr(result, 'global_step') else 0
            print(f"\n{'='*80}")
            print(f"🔍 训练完成诊断:")
            print(f"   实际训练步数: {actual_steps}")
            print(f"   预期训练步数: {total_steps}")

            if actual_steps < total_steps:
                print(f"\n⚠️  警告: 训练提前结束!")
                print(f"   实际步数 ({actual_steps}) < 预期步数 ({total_steps})")
                print(f"   可能原因:")
                print(f"   1. max_steps 参数限制")
                print(f"   2. 内存不足导致崩溃")
                print(f"   3. 设备兼容性问题")

            print(f"{'='*80}")
            print("✅ SFT训练完成")

            return self.trainer

        except Exception as e:
            print(f"\n{'='*80}")
            print(f"❌ 训练过程中发生异常:")
            print(f"   异常信息: {str(e)}")
            print(f"   类型: {type(e).__name__}")
            print(f"{'='*80}")
            raise


class GRPOTrainerWrapper(BaseTrainerWrapper):
    """GRPO (Group Relative Policy Optimization) 训练器封装
    
    用于强化学习训练，优化模型的推理能力。
    GRPO相比PPO更简单，不需要Value Model。
    """
    
    def __init__(
        self,
        config: Optional[TrainingConfig] = None,
        dataset = None,
        reward_fn: Optional[Callable] = None
    ):
        """
        初始化GRPO训练器
        
        Args:
            config: 训练配置
            dataset: 训练数据集
            reward_fn: 奖励函数
        """
        super().__init__(config)
        self.dataset = dataset
        self.reward_fn = reward_fn
    
    def setup_model(self):
        """设置模型和tokenizer"""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        print(f"📦 加载模型: {self.config.model_name}")
        
        # 加载tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # 加载模型
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            trust_remote_code=True,
            device_map="auto" if self.config.use_fp16 or self.config.use_bf16 else None
        )
        
        print("✅ 模型加载完成")
    
    def train(self):
        """开始GRPO训练"""
        from trl import GRPOConfig, GRPOTrainer
        import torch

        if self.model is None:
            self.setup_model()

        if self.dataset is None:
            raise ValueError("数据集未设置，请提供训练数据集")

        if self.reward_fn is None:
            raise ValueError("奖励函数未设置，请提供reward_fn")

        # 🔍 诊断：检测设备类型
        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"

        print(f"\n{'='*80}")
        print(f"🔍 诊断信息:")
        print(f"   设备类型: {device}")
        print(f"   数据集大小: {len(self.dataset)}")
        print(f"   训练轮数: {self.config.num_train_epochs}")
        print(f"   批次大小: {self.config.per_device_train_batch_size}")
        print(f"   梯度累积步数: {self.config.gradient_accumulation_steps}")
        print(f"{'='*80}\n")

        # 确定report_to参数
        report_to = []
        if self.config.use_wandb:
            report_to.append("wandb")
        if self.config.use_tensorboard:
            report_to.append("tensorboard")
        if not report_to:
            report_to = ["none"]

        # 🔍 修复：MPS 设备需要禁用 pin_memory
        dataloader_pin_memory = device != "mps"

        # 配置训练参数
        training_args = GRPOConfig(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            fp16=self.config.use_fp16 and device == "cuda",  # fp16 仅在 CUDA 上启用
            bf16=self.config.use_bf16 and device == "cuda",  # bf16 仅在 CUDA 上启用
            report_to=report_to,
            remove_unused_columns=False,
            dataloader_pin_memory=dataloader_pin_memory,  # 修复 MPS 兼容性
        )

        # 计算总步数
        total_steps = (
            len(self.dataset) //
            (self.config.per_device_train_batch_size * self.config.gradient_accumulation_steps)
        ) * self.config.num_train_epochs

        # 创建详细日志回调
        logging_callback = DetailedLoggingCallback(
            total_steps=total_steps,
            num_epochs=self.config.num_train_epochs
        )

        # 创建训练器
        self.trainer = GRPOTrainer(
            model=self.model,
            args=training_args,
            train_dataset=self.dataset,
            reward_funcs=self.reward_fn,
            processing_class=self.tokenizer,
            callbacks=[logging_callback],
        )

        print("\n🚀 开始GRPO训练...")
        print(f"{'='*80}\n")

        try:
            result = self.trainer.train()

            # 检查训练是否真的完成
            actual_steps = result.global_step if hasattr(result, 'global_step') else 0
            print(f"\n{'='*80}")
            print(f"🔍 训练完成诊断:")
            print(f"   实际训练步数: {actual_steps}")
            print(f"   预期训练步数: {total_steps}")

            if actual_steps < total_steps:
                print(f"\n⚠️  警告: 训练提前结束!")
                print(f"   实际步数 ({actual_steps}) < 预期步数 ({total_steps})")

            print(f"{'='*80}")
            print("✅ GRPO训练完成")

            return self.trainer

        except Exception as e:
            print(f"\n{'='*80}")
            print(f"❌ 训练过程中发生异常:")
            print(f"   异常信息: {str(e)}")
            print(f"   类型: {type(e).__name__}")
            print(f"{'='*80}")
            raise


class PPOTrainerWrapper(BaseTrainerWrapper):
    """PPO (Proximal Policy Optimization) 训练器封装
    
    用于强化学习训练，是经典的RL算法。
    相比GRPO，PPO需要额外的Value Model，但可能获得更好的性能。
    """
    
    def __init__(
        self,
        config: Optional[TrainingConfig] = None,
        dataset = None,
        reward_model = None
    ):
        """
        初始化PPO训练器
        
        Args:
            config: 训练配置
            dataset: 训练数据集
            reward_model: 奖励模型
        """
        super().__init__(config)
        self.dataset = dataset
        self.reward_model = reward_model
    
    def setup_model(self):
        """设置模型和tokenizer"""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        print(f"📦 加载模型: {self.config.model_name}")
        
        # 加载tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # 加载模型
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            trust_remote_code=True,
            device_map="auto" if self.config.use_fp16 or self.config.use_bf16 else None
        )
        
        print("✅ 模型加载完成")
    
    def train(self):
        """开始PPO训练"""
        print("⚠️  PPO训练器正在开发中...")
        print("   建议使用GRPO训练器，它更简单且性能相近")
        raise NotImplementedError("PPO训练器尚未实现，请使用GRPOTrainerWrapper")

