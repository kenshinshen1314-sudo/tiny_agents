"""
简化版记忆检索测试 - 用于调试

测试添加记忆后立即检索，检查数据流
"""

import os
import logging

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

# 设置环境变量
os.environ['QDRANT_URL'] = "https://175cf2f6-d9cf-428d-966e-93afa5a2a66c.us-west-1-0.aws.cloud.qdrant.io:443"
os.environ['QDRANT_API_KEY'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.1ymm64eBVHTAgqvao-0Y4sA5V7fxvXA4zgptMsD3Vxg"

from tiny_agents.tools.builtin.memory_tool import MemoryTool

print("=" * 60)
print("测试：添加记忆后立即检索")
print("=" * 60)

# 创建记忆工具
memory_tool = MemoryTool(user_id="test_user_debug")

# 1. 添加一条测试记忆
print("\n1️⃣ 添加测试记忆...")
test_content = "测试内容：这是一条关于人工智能的记忆"
add_result = memory_tool.execute(
    action="add",
    content=test_content,
    memory_type="semantic",
    importance=0.8
)
print(f"添加结果: {add_result}")

# 2. 立即检索这条记忆
print("\n2️⃣ 检索刚添加的记忆...")
search_result = memory_tool.execute(
    action="search",
    query="人工智能",
    limit=5,
    memory_type="semantic"
)
print(f"检索结果:\n{search_result}")

# 3. 检查记忆摘要
print("\n3️⃣ 获取记忆摘要...")
summary_result = memory_tool.execute("summary")
print(f"摘要:\n{summary_result}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
