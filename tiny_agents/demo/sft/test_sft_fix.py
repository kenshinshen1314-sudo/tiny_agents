"""测试 SFT 训练修复

快速验证 SFT 训练诊断与修复是否有效。
使用小数据集 (max_samples=20) 进行快速测试。
"""

from tiny_agents.rl import (
    SFTTrainerWrapper,
    TrainingConfig,
    create_sft_dataset,
    setup_training_environment
)


def test_sft_training():
    """测试 SFT 训练"""

    print("=" * 80)
    print("🧪 SFT 训练修复测试")
    print("=" * 80)

    # 创建配置 - 使用小数据集快速测试
    config = TrainingConfig(
        model_name="Qwen/Qwen2-0.5B-Instruct",
        output_dir="./test_output/sft_fix",
        num_train_epochs=2,  # 2 个 epoch
        per_device_train_batch_size=4,  # 小批次
        gradient_accumulation_steps=2,  # 梯度累积
        learning_rate=5e-5,
        warmup_steps=2,  # 减少预热步数
        logging_steps=1,  # 每步都记录日志
        save_steps=100,  # 减少保存频率
        use_lora=True,  # 使用 LoRA
        gradient_checkpointing=True,
    )

    # 设置环境
    setup_training_environment(config)

    # 加载小数据集
    print("\n📥 加载测试数据集 (max_samples=20)...")
    dataset = create_sft_dataset(max_samples=20)
    print(f"✅ 数据集加载完成: {len(dataset)} 个样本")

    # 预期步数计算
    expected_steps = (
        len(dataset) //
        (config.per_device_train_batch_size * config.gradient_accumulation_steps)
    ) * config.num_train_epochs

    print(f"\n📊 预期训练步数: {expected_steps}")
    print(f"   数据集: {len(dataset)} 样本")
    print(f"   批次大小: {config.per_device_train_batch_size}")
    print(f"   梯度累积: {config.gradient_accumulation_steps}")
    print(f"   训练轮数: {config.num_train_epochs}")
    print(f"\n   计算: {len(dataset)} / ({config.per_device_train_batch_size} × {config.gradient_accumulation_steps}) × {config.num_train_epochs} = {expected_steps}")

    # 创建训练器
    trainer_wrapper = SFTTrainerWrapper(config=config, dataset=dataset)

    # 开始训练
    print("\n🚀 开始训练...")
    print("=" * 80)

    try:
        result = trainer_wrapper.train()

        # 验证结果
        actual_steps = result.state.global_step if hasattr(result.state, 'global_step') else 0

        print("\n" + "=" * 80)
        print("🎯 测试结果验证")
        print("=" * 80)
        print(f"   预期步数: {expected_steps}")
        print(f"   实际步数: {actual_steps}")

        if actual_steps == expected_steps:
            print(f"\n✅ 测试通过! 训练按预期完成 {actual_steps} 步")
        elif actual_steps > expected_steps:
            print(f"\n✅ 测试通过! 训练完成了 {actual_steps} 步 (超过预期)")
        else:
            print(f"\n⚠️  测试警告! 训练提前结束: {actual_steps}/{expected_steps} 步")
            print(f"   需要进一步诊断")

        # 保存模型
        trainer_wrapper.save_model()

        print("\n✅ 测试完成!")

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ 测试失败!")
        print(f"   异常: {type(e).__name__}")
        print(f"   信息: {str(e)}")
        print("=" * 80)
        raise


if __name__ == "__main__":
    test_sft_training()
