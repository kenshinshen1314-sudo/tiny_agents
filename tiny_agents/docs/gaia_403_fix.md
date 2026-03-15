# GAIA数据集下载403错误修复指南

## 问题描述

从HuggingFace下载GAIA数据集时遇到403 Forbidden错误。

## 根本原因

GAIA是一个**受限数据集（gated repo）**，需要：
1. 在HuggingFace上申请访问权限
2. 使用HF_TOKEN进行认证
3. 使用官方端点（不能使用镜像站点）

由于系统中设置了 `HF_ENDPOINT="https://hf-mirror.com"` 环境变量，所有HuggingFace请求都转发到镜像站点，而镜像站点**不支持gated dataset的认证机制**。

## 修复方案

### ✅ 方案1：代码修改（已实施）

**状态**: 已完成

**修改文件**: `evaluation/benchmarks/gaia/dataset.py`

**修改内容**: 在 `snapshot_download` 调用中添加 `endpoint="https://huggingface.co"` 参数

```python
snapshot_download(
    repo_id=self.dataset_name,
    repo_type="dataset",
    local_dir=str(local_dir),
    token=hf_token,
    endpoint="https://huggingface.co",  # 强制使用官方端点（gated dataset需要认证）
    local_dir_use_symlinks=False
)
```

**优点**:
- 无需每次设置环境变量
- 对GAIA数据集自动使用正确的端点
- 不影响其他HuggingFace操作

### 方案2：临时禁用镜像（备选方案）

如果方案1无法使用，可以在运行时临时禁用镜像：

```bash
# 方法1：运行时覆盖环境变量
HF_ENDPOINT="" python demo/gaia/gaia_quick_start.py

# 方法2：当前会话禁用
unset HF_ENDPOINT
python demo/gaia/gaia_quick_start.py
```

### 方案3：永久禁用镜像（可选）

如果不需要HuggingFace镜像站点，可以从shell配置中删除：

```bash
# 编辑 ~/.zshrc，注释或删除以下行：
# export HF_ENDPOINT="https://hf-mirror.com"

# 重新加载配置
source ~/.zshrc
```

## 前置条件

### 1. HuggingFace访问权限

必须先在HuggingFace上申请GAIA访问权限：
- 访问：https://huggingface.co/datasets/gaia-benchmark/GAIA
- 点击 "Request access" 申请访问
- 等待审批通过（通常几分钟到几小时）

### 2. HF_TOKEN环境变量

确保已设置有效的HF_TOKEN：

```bash
# 方法1：在.env文件中设置
echo "HF_TOKEN=your_token_here" >> .env

# 方法2：导出环境变量
export HF_TOKEN="your_token_here"

# 方法3：在运行时设置
HF_TOKEN="your_token_here" python demo/gaia/gaia_quick_start.py
```

## 验证修复

### 方法1：运行验证脚本

```bash
bash test_gaia_fix.sh
```

### 方法2：直接运行GAIA评估

```bash
# 使用代码修改后的版本（推荐）
python demo/gaia/gaia_quick_start.py

# 或者临时禁用镜像
HF_ENDPOINT="" python demo/gaia/gaia_quick_start.py
```

### 预期输出

```
✅ GAIA数据集加载完成
   数据源: gaia-benchmark/GAIA
   分割: validation
   级别: 1
   样本数: X
```

## 故障排查

### 错误1: 403 Forbidden

**原因**: 未申请GAIA访问权限或HF_TOKEN无效

**解决**:
1. 确认已在 https://huggingface.co/datasets/gaia-benchmark/GAIA 申请访问
2. 确认HF_TOKEN有效且已授权访问GAIA
3. 检查代码是否使用了正确的endpoint参数

### 错误2: HF_TOKEN not found

**原因**: 未设置HF_TOKEN环境变量

**解决**:
```bash
export HF_TOKEN="your_token_here"
```

### 错误3: Repository not found

**原因**: 数据集名称错误或权限问题

**解决**:
1. 确认使用正确的数据集名称：`gaia-benchmark/GAIA`
2. 确认已获得访问权限

## 相关文件

- **数据集加载器**: `evaluation/benchmarks/gaia/dataset.py`
- **GAIA评估工具**: `tools/builtin/gaia_evaluation_tool.py`
- **快速开始示例**: `demo/gaia/gaia_quick_start.py`
- **验证脚本**: `test_gaia_fix.sh`

## 参考资料

- [GAIA Benchmark官网](https://huggingface.co/datasets/gaia-benchmark/GAIA)
- [HuggingFace Gated Datasets文档](https://huggingface.co/docs/hub/security-gated)
- [snapshot_download API文档](https://huggingface.co/docs/huggingface_hub/guides/download)
