"""
多模态文档 RAG Demo

展示如何使用 RAG 工具处理多种格式的文档：
- 📝 文本 (Text)
- 📄 PDF 文档
- 🖼️ 图片 (OCR提取文字)
- 🎵 音频 (语音转文字)
- 📊 Office 文档 (Word, Excel, PPT)

运行方式:
    # 交互式模式（无参数）
    python demo/multimodal_rag_demo.py

    # 添加单个文件
    python demo/multimodal_rag_demo.py --add 文件路径

    # 添加多个文件
    python demo/multimodal_rag_demo.py --add 文件1.pdf 文件2.docx

    # 添加整个目录
    python demo/multimodal_rag_demo.py --add-dir ./my_docs

    # 搜索知识库
    python demo/multimodal_rag_demo.py --search "查询内容"

    # 智能问答
    python demo/multimodal_rag_demo.py --ask "问题内容"

    # 查看统计
    python demo/multimodal_rag_demo.py --stats

    # 清空知识库
    python demo/multimodal_rag_demo.py --clear

或直接在 Python 中导入使用:
    from demo.multimodal_rag_demo import MultimodalRAGDemo

    # 方式1: 创建实例后调用方法
    demo = MultimodalRAGDemo()
    demo.add_file("path/to/document.pdf")
    demo.search("查询内容")

    # 方式2: 完整演示流程
    demo.run_demo()
"""

import os
import sys
import argparse
from typing import List, Optional

# 确保可以导入 tiny_agents
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tiny_agents.tools.builtin.rag_tool import RAGTool


# 支持的文件格式
SUPPORTED_EXTENSIONS = {
    # 文档
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    # 文本
    '.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm',
    # 图片 (OCR)
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
    # 音频 (语音转文字)
    '.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg',
    # 代码
    '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.css', '.scss',
    # 其他
    '.log', '.conf', '.ini', '.cfg', '.yaml', '.yml', '.toml',
    '.zip', '.tar', '.gz', '.rar'
}


class MultimodalRAGDemo:
    """多模态文档 RAG 演示类"""

    def __init__(
        self,
        namespace: str = "multimodal_demo",
        knowledge_base_path: str = "./multimodal_knowledge_base",
        collection_name: str = "multimodal_collection"
    ):
        """初始化多模态 RAG 演示

        Args:
            namespace: 知识库命名空间
            knowledge_base_path: 知识库存储路径
            collection_name: 集合名称
        """
        self.namespace = namespace
        self.knowledge_base_path = knowledge_base_path
        self.collection_name = collection_name

        # 创建 RAG 工具实例
        self.rag = RAGTool(
            knowledge_base_path=knowledge_base_path,
            collection_name=collection_name,
            rag_namespace=namespace
        )

        print("=" * 60)
        print("🚀 多模态文档 RAG 系统初始化完成")
        print(f"📂 知识库路径: {knowledge_base_path}")
        print(f"📋 集合名称: {collection_name}")
        print(f"📝 命名空间: {namespace}")
        print("=" * 60)

    def is_supported_file(self, file_path: str) -> bool:
        """检查文件是否支持"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in SUPPORTED_EXTENSIONS

    def get_file_type(self, file_path: str) -> str:
        """根据文件扩展名判断文件类型"""
        ext = os.path.splitext(file_path)[1].lower()

        type_mapping = {
            '.pdf': '📄 PDF',
            '.doc': '📝 Word',
            '.docx': '📝 Word',
            '.xls': '📊 Excel',
            '.xlsx': '📊 Excel',
            '.ppt': '📑 PPT',
            '.pptx': '📑 PPT',
            '.txt': '📝 文本',
            '.md': '📝 Markdown',
            '.csv': '📊 CSV',
            '.json': '📋 JSON',
            '.xml': '📋 XML',
            '.html': '🌐 HTML',
            '.htm': '🌐 HTML',
            '.jpg': '🖼️ 图片',
            '.jpeg': '🖼️ 图片',
            '.png': '🖼️ 图片',
            '.gif': '🖼️ 图片',
            '.bmp': '🖼️ 图片',
            '.tiff': '🖼️ 图片',
            '.tif': '🖼️ 图片',
            '.webp': '🖼️ 图片',
            '.mp3': '🎵 音频',
            '.wav': '🎵 音频',
            '.m4a': '🎵 音频',
            '.aac': '🎵 音频',
            '.flac': '🎵 音频',
            '.ogg': '🎵 音频',
            '.zip': '📦 ZIP',
            '.tar': '📦 TAR',
            '.gz': '📦 GZ',
            '.rar': '📦 RAR',
        }

        return type_mapping.get(ext, '📄 其他')

    def add_file(self, file_path: str) -> str:
        """添加单个文件到知识库

        Args:
            file_path: 文件路径

        Returns:
            执行结果
        """
        if not os.path.exists(file_path):
            return f"❌ 文件不存在: {file_path}"

        if not self.is_supported_file(file_path):
            return f"❌ 不支持的文件格式: {os.path.splitext(file_path)[1]}"

        file_type = self.get_file_type(file_path)
        print(f"  {file_type} 添加: {os.path.basename(file_path)}")

        result = self.rag.add_document(
            file_path=file_path,
            namespace=self.namespace
        )
        return result

    def add_files(self, file_paths: List[str]) -> str:
        """批量添加多个文件

        Args:
            file_paths: 文件路径列表

        Returns:
            执行结果
        """
        if not file_paths:
            return "❌ 文件列表为空"

        successful = 0
        failed = 0
        results = []

        for file_path in file_paths:
            result = self.add_file(file_path)
            if result.startswith("✅"):
                successful += 1
                results.append(f"  ✅ {os.path.basename(file_path)}")
            elif result.startswith("⚠️"):
                successful += 1
                results.append(f"  ⚠️ {os.path.basename(file_path)}")
            else:
                failed += 1
                results.append(f"  ❌ {os.path.basename(file_path)}: {result}")

        summary = [
            f"\n📊 添加完成: 成功 {successful}, 失败 {failed}",
            "\n详细结果:"
        ]
        summary.extend(results)

        return "\n".join(summary)

    def add_directory(self, dir_path: str, recursive: bool = True) -> str:
        """添加目录下的所有支持的文件

        Args:
            dir_path: 目录路径
            recursive: 是否递归搜索子目录

        Returns:
            执行结果
        """
        if not os.path.exists(dir_path):
            return f"❌ 目录不存在: {dir_path}"

        if not os.path.isdir(dir_path):
            return f"❌ 不是有效目录: {dir_path}"

        file_paths = []

        if recursive:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.is_supported_file(file_path):
                        file_paths.append(file_path)
        else:
            for file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path) and self.is_supported_file(file_path):
                    file_paths.append(file_path)

        if not file_paths:
            return f"❌ 目录中没有找到支持的文件: {dir_path}"

        print(f"\n📂 找到 {len(file_paths)} 个支持的文件")
        return self.add_files(file_paths)

    def add_text(self, text: str, document_id: Optional[str] = None) -> str:
        """添加文本内容

        Args:
            text: 文本内容
            document_id: 文档ID（可选）

        Returns:
            执行结果
        """
        return self.rag.add_text(
            text=text,
            document_id=document_id,
            namespace=self.namespace
        )

    def search(self, query: str, limit: int = 5) -> str:
        """搜索知识库

        Args:
            query: 查询内容
            limit: 返回结果数量

        Returns:
            搜索结果
        """
        print(f"\n🔍 搜索: 「{query}」")
        print("-" * 40)
        return self.rag.search(
            query=query,
            namespace=self.namespace,
            limit=limit
        )

    def ask(self, question: str, limit: int = 3) -> str:
        """智能问答

        Args:
            question: 问题
            limit: 检索结果数量

        Returns:
            问答结果
        """
        print(f"\n💬 问答: {question}")
        print("-" * 40)
        return self.rag.ask(
            question=question,
            namespace=self.namespace,
            limit=limit
        )

    def get_stats(self) -> str:
        """获取知识库统计"""
        return self.rag.execute("stats", namespace=self.namespace)

    def clear(self, confirm: bool = True) -> str:
        """清空知识库

        Args:
            confirm: 是否确认清空

        Returns:
            执行结果
        """
        return self.rag.execute(
            "clear",
            confirm=confirm,
            namespace=self.namespace
        )

    # ============================================================
    # 演示功能
    # ============================================================

    def run_demo(self, include_sample_data: bool = True):
        """运行完整的演示流程

        Args:
            include_sample_data: 是否包含示例数据
        """
        print("\n" + "🎯" * 30)
        print("欢迎使用多模态文档 RAG 系统演示")
        print("🎯" * 30)

        if include_sample_data:
            self._add_sample_data()

        # 搜索演示
        self._demo_search()

        # 智能问答演示
        self._demo_ask()

        # 显示统计信息
        self.show_stats()

        print("\n" + "✅" * 30)
        print("演示完成！")
        print("✅" * 30)

    def _add_sample_data(self):
        """添加示例数据"""
        print("\n" + "=" * 60)
        print("📝 添加示例数据")
        print("=" * 60)

        texts = [
            {
                "id": "python_intro",
                "content": """Python是一种高级编程语言，由Guido van Rossum于1991年首次发布。
Python的设计哲学强调代码的可读性和简洁的语法。
相比于C++或Java，Python让开发者能够用更少的代码表达想法。
Python支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。"""
            },
            {
                "id": "ml_overview",
                "content": """机器学习是人工智能的一个分支，通过算法让计算机从数据中学习模式。
机器学习主要包括三种类型：监督学习、无监督学习和强化学习。
监督学习需要带标签的训练数据，用于分类和回归任务。
无监督学习处理无标签数据，用于聚类和降维。
强化学习通过与环境交互来学习最优策略。"""
            },
            {
                "id": "rag_intro",
                "content": """RAG（检索增强生成）是一种结合信息检索和文本生成的AI技术。
RAG通过检索相关知识来增强大语言模型的生成能力。
RAG的核心组件包括：向量数据库、嵌入模型和检索算法。
使用RAG可以解决LLM的幻觉问题和知识时效性问题。"""
            },
            {
                "id": "multimodal_ai",
                "content": """多模态AI是指能够处理和理解多种类型数据的AI系统。
常见模态包括：文本、图像、音频、视频和触觉等。
多模态大模型如GPT-4V可以同时理解图像和文本。
多模态RAG可以处理PDF、图片、音频等非纯文本格式的文档。"""
            }
        ]

        for text_item in texts:
            result = self.rag.add_text(
                text=text_item["content"],
                document_id=text_item["id"],
                namespace=self.namespace
            )
            print(f"  ✅ {text_item['id']}: {result.split('\n')[0]}")

    def _demo_search(self):
        """演示搜索功能"""
        print("\n" + "=" * 60)
        print("🔍 演示：搜索知识库")
        print("=" * 60)

        search_queries = [
            "Python 编程语言特点",
            "机器学习有哪些类型",
            "RAG 技术是什么",
        ]

        for query in search_queries:
            result = self.search(query, limit=2)
            print(result)

    def _demo_ask(self):
        """演示智能问答"""
        print("\n" + "=" * 60)
        print("💬 演示：智能问答")
        print("=" * 60)

        questions = [
            "Python 适合开发什么类型的应用？",
            "RAG 技术如何解决大模型的幻觉问题？",
        ]

        for question in questions:
            result = self.ask(question, limit=3)
            print(result)

    def show_stats(self):
        """显示知识库统计"""
        print("\n" + "=" * 60)
        print("📊 知识库统计信息")
        print("=" * 60)
        print(self.get_stats())


def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(
        description="多模态文档 RAG 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式模式
  python demo/multimodal_rag_demo.py

  # 添加单个文件
  python demo/multimodal_rag_demo.py --add document.pdf

  # 添加多个文件
  python demo/multimodal_rag_demo.py --add file1.pdf file2.docx "my file.txt"

  # 添加目录
  python demo/multimodal_rag_demo.py --add-dir ./documents

  # 添加文本
  python demo/multimodal_rag_demo.py --add-text "这是要添加的文本内容"

  # 搜索
  python demo/multimodal_rag_demo.py --search "查询内容"

  # 问答
  python demo/multimodal_rag_demo.py --ask "问题内容"

  # 查看统计
  python demo/multimodal_rag_demo.py --stats

  # 清空知识库
  python demo/multimodal_rag_demo.py --clear

  # 运行完整演示
  python demo/multimodal_rag_demo.py --demo
        """
    )

    # 添加文件相关参数
    parser.add_argument(
        '--add', '--file', '-a',
        nargs='+',
        metavar='FILE',
        help='添加文件到知识库（支持多个文件）'
    )

    # 添加目录参数
    parser.add_argument(
        '--add-dir', '--directory', '-d',
        metavar='DIRECTORY',
        help='添加目录下所有支持的文件'
    )

    # 添加文本参数
    parser.add_argument(
        '--add-text', '--text', '-t',
        metavar='TEXT',
        help='添加文本内容到知识库'
    )

    # 搜索参数
    parser.add_argument(
        '--search', '-s',
        metavar='QUERY',
        help='搜索知识库'
    )

    # 问答参数
    parser.add_argument(
        '--ask', '-k',
        metavar='QUESTION',
        help='智能问答'
    )

    # 统计参数
    parser.add_argument(
        '--stats', '--stat',
        action='store_true',
        help='查看知识库统计信息'
    )

    # 清空参数
    parser.add_argument(
        '--clear', '-c',
        action='store_true',
        help='清空知识库'
    )

    # 演示参数
    parser.add_argument(
        '--demo', '--run-demo',
        action='store_true',
        help='运行完整演示流程'
    )

    # 命名空间参数
    parser.add_argument(
        '--namespace', '-n',
        default='multimodal_demo',
        help='知识库命名空间 (默认: multimodal_demo)'
    )

    # 知识库路径参数
    parser.add_argument(
        '--kb-path', '--knowledge-base',
        default='./multimodal_knowledge_base',
        help='知识库存储路径 (默认: ./multimodal_knowledge_base)'
    )

    # 集合名称参数
    parser.add_argument(
        '--collection', '--coll',
        default='multimodal_collection',
        help='集合名称 (默认: multimodal_collection)'
    )

    args = parser.parse_args()

    # 创建 RAG Demo 实例
    demo = MultimodalRAGDemo(
        namespace=args.namespace,
        knowledge_base_path=args.kb_path,
        collection_name=args.collection
    )

    # 执行操作
    has_operation = False

    # 添加文件
    if args.add:
        has_operation = True
        result = demo.add_files(args.add)
        print(result)

    # 添加目录
    if args.add_dir:
        has_operation = True
        result = demo.add_directory(args.add_dir)
        print(result)

    # 添加文本
    if args.add_text:
        has_operation = True
        result = demo.add_text(args.add_text)
        print(result)

    # 搜索
    if args.search:
        has_operation = True
        result = demo.search(args.search)
        print(result)

    # 问答
    if args.ask:
        has_operation = True
        result = demo.ask(args.ask)
        print(result)

    # 统计
    if args.stats:
        has_operation = True
        result = demo.get_stats()
        print(result)

    # 清空
    if args.clear:
        has_operation = True
        result = demo.clear(confirm=True)
        print(result)

    # 运行演示
    if args.demo:
        has_operation = True
        demo.run_demo(include_sample_data=True)

    # 无参数时运行交互式模式
    if not has_operation:
        # 先检查是否有示例数据需要添加
        sample_dir = os.path.join(os.path.dirname(__file__), "samples")
        has_sample_files = False

        if os.path.exists(sample_dir):
            sample_files = [
                os.path.join(sample_dir, f)
                for f in os.listdir(sample_dir)
                if demo.is_supported_file(f)
            ]
            has_sample_files = len(sample_files) > 0

        if has_sample_files:
            print("\n📂 发现示例文件，是否添加到知识库？")
            result = demo.add_directory(sample_dir)
            print(result)

        # 运行演示
        demo.run_demo(include_sample_data=not has_sample_files)


if __name__ == "__main__":
    main()
