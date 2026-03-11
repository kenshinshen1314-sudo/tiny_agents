
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import time
import json

from tiny_agents.tools.builtin.memory_tool import MemoryTool
from tiny_agents.tools.builtin.rag_tool import RAGTool
from tiny_agents.core.llm import HelloAgentsLLM


class PDFParserAssistant:
    """智能文档解析助手，结合记忆工具和RAG工具实现文档加载、知识提取和问答功能"""

    def __init__(self, user_id: str = "default_user"):
        """
        初始化PDF解析助手

        Args:
            user_id (str, optional): 用户ID，用于区分不同用户的会话和记忆. 默认值为"default_user".
        """
        self.user_id = user_id
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        # 初始化记忆工具和RAG工具
        self.memory_tool = MemoryTool(user_id=self.user_id)
        self.rag_tool = RAGTool(rag_namespace=f"pdf_parser_{self.user_id}")
        # 初始化 LLM 用于生成建议问题
        self.llm = HelloAgentsLLM()
        # 初始化统计信息
        self.stats = {
            "session_start": datetime.now(),
            "documents_loaded": 0,
            "questions_asked": 0,
            "concepts_learned": 0
        }
        # 当前加载的文档信息
        self.current_document = None

    def load_document(self, pdf_path: str) -> Dict[str, Any]:
        """
        加载PDF文档到RAG知识库

        Args:
            pdf_path (str): PDF文件的路径

        Returns:
            Dict[str, Any]: 包含加载结果的字典，成功时包含文档信息，失败时包含错误消息
        """
        if not os.path.exists(pdf_path):
            return {"success": False, "message": f"文件不存在或未找到: {pdf_path}"}

        start_time = time.time()

        # 处理PDF： MarkItDown -> 智能分块 -> 向量化存储
        # 注意：rag_tool.execute 返回字符串，需要解析结果
        result_str = self.rag_tool.execute(
            action="add_document",
            file_path=pdf_path,
            chunk_size=1000,
            chunk_overlap=200
        )

        end_time = time.time()
        process_time = end_time - start_time

        # 检查是否成功（RAGTool 返回的字符串包含 ✅ 表示成功）
        if "✅" in result_str or "文档已添加" in result_str:
            self.current_document = os.path.basename(pdf_path)
            self.stats["documents_loaded"] += 1
            # 记录加载文档的情景记忆
            self.memory_tool.execute(
                action="add",
                content=f"加载文档成功 {self.current_document}",
                memory_type="episodic",
                importance=0.9,
                event_type="document_load",
                session_id=self.session_id
            )

            return {
                "success": True,
                "message": f"文档加载成功! (耗时 {process_time:.2f} 秒)\n{result_str}",
                "document": self.current_document
            }
        else:
            return {
                "success": False,
                "message": f"文档加载失败: {result_str}"
            }

    def ask(self, question: str, use_advanced_search: bool = True) -> str:
        """
        向文档助手提问并获取回答

        Args:
            question (str): 用户的问题
            use_advanced_search (bool, optional): 是否使用高级搜索(MQE+HyDE). 默认值为True

        Returns:
            str: 答案
        """
        if not self.current_document:
            return "请先加载文档！！！"

        start_time = time.time()

        # 记录问题到工作记忆
        self.memory_tool.execute(
            action="add",
            content=f"问题: {question}",
            memory_type="working",
            importance=0.6,
            session_id=self.session_id
        )

        # 从RAG知识库中检索相关知识
        answer = self.rag_tool.execute(
            action="ask",
            query=question,
            question=question,
            limit=5,
            enable_advanced_search=use_advanced_search,
            enable_mqe=use_advanced_search,
            enable_hyde=use_advanced_search
        )

        # 记录到情景记忆
        self.memory_tool.execute(
                action="add",
                content=f"关于 '{question}' 的学习",
                memory_type="episodic",
                importance=0.7,
                event_type="qa_interaction",
                session_id=self.session_id
            )

        self.stats["questions_asked"] += 1

        end_time = time.time()
        process_time = end_time - start_time

        return answer

    def add_note(self, content: str, concept: Optional[str] = None):
        """
        添加学习笔记到记忆工具

        Args:
            content (str): 学习笔记的内容
            concept (str, optional): 相关概念
        """
        self.memory_tool.execute(
            action="add",
            content=content,
            memory_type="semantic",
            importance=0.8,
            concept=concept or "general",
            session_id=self.session_id
        )
        self.stats["concepts_learned"] += 1

    def recall(self, query: str, limit: int = 5) -> str:
        """
        从记忆工具中回忆相关信息

        Args:
            query (str): 回忆查询的关键词或问题
            limit (int, optional): 返回的相关记忆条数. 默认值为5

        Returns:
            str: 回忆结果的摘要
        """
        results = self.memory_tool.execute(
            action="query_points",
            query=query,
            limit=limit,
            user_id=self.user_id
        )
        if results:
            return f"回忆到以下相关信息:\n" + "\n".join([f"- {item['content']} (重要性: {item['importance']})" for item in results])
        else:
            return "没有找到相关的记忆信息。"

    def get_stats(self) -> Dict[str, Any]:
        """获取学习统计"""
        duration = (datetime.now() - self.stats["session_start"]).total_seconds()

        return {
            "会话时长": f"{duration:.0f}秒",
            "加载文档": self.stats["documents_loaded"],
            "提问次数": self.stats["questions_asked"],
            "学习笔记": self.stats["concepts_learned"],
            "当前文档": self.current_document or "未加载"
        }

    def generate_report(self, save_to_file: bool = True) -> Dict[str, Any]:
        """生成学习报告"""
        memory_summary = self.memory_tool.execute("summary", limit=10)
        rag_stats = self.rag_tool.execute("stats")

        duration = (datetime.now() - self.stats["session_start"]).total_seconds()
        report = {
            "session_info": {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "start_time": self.stats["session_start"].isoformat(),
                "duration_seconds": duration
            },
            "learning_metrics": {
                "documents_loaded": self.stats["documents_loaded"],
                "questions_asked": self.stats["questions_asked"],
                "concepts_learned": self.stats["concepts_learned"]
            },
            "memory_summary": memory_summary,
            "rag_status": rag_stats
        }

        if save_to_file:
            report_dir = os.path.join(os.path.dirname(__file__), "report")
            os.makedirs(report_dir, exist_ok=True)
            report_file = os.path.join(report_dir, f"learning_report_{self.session_id}.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)

            report["report_file"] = report_file

        return report

    def generate_suggestions(self, num_questions: int = 5) -> List[str]:
        """
        根据已加载的文档内容生成建议问题

        Args:
            num_questions (int): 要生成的问题数量，默认为5

        Returns:
            List[str]: 建议问题列表
        """
        if not self.current_document:
            return []

        try:
            # 使用 RAG 工具搜索文档内容片段
            search_results = self.rag_tool.execute(
                action="search",
                query="核心内容 主要观点 关键概念 重要结论",
                limit=num_questions * 2,
                enable_advanced_search=False
            )

            # 提取文档片段作为上下文
            context_parts = []
            if isinstance(search_results, str):
                lines = search_results.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('搜索结果') and not line.startswith('文档:'):
                        cleaned = line.strip()
                        if cleaned and len(cleaned) > 20:
                            context_parts.append(cleaned)
                            if len(context_parts) >= 3:
                                break

            if not context_parts:
                return [
                    "这个文档的主要内容是什么？",
                    "文档中提到了哪些核心概念？",
                    "能总结一下文档的要点吗？",
                    "文档中有什么重要的结论？",
                    "解释一下文档中的关键术语"
                ]

            context = "\n\n".join(context_parts[:3])

            # 使用 LLM 生成建议问题
            prompt = f"""基于以下文档片段，生成 {num_questions} 个用户可能感兴趣的探索性问题。

要求：
1. 问题应该基于文档内容，但不是简单的"是什么"
2. 问题应该引导用户深入理解文档
3. 问题应该具体、有针对性
4. 每个问题独立成行，不要编号
5. 问题要简洁明了，不超过20个字

文档片段：
{context}

请生成 {num_questions} 个问题："""

            response = self.llm.invoke([{"role": "user", "content": prompt}])

            if response:
                questions = []
                for line in response.split('\n'):
                    line = line.strip()
                    cleaned = line
                    for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '•', '-', '*', '？', '?']:
                        if cleaned.startswith(prefix):
                            cleaned = cleaned[1:].strip()
                            break

                    if cleaned and len(cleaned) > 5 and len(cleaned) < 50:
                        if not cleaned.endswith('？') and not cleaned.endswith('?'):
                            cleaned += '？'
                        questions.append(cleaned)

                        if len(questions) >= num_questions:
                            break

                default_questions = [
                    "文档的核心观点是什么？",
                    "有哪些关键术语需要理解？",
                    "文档得出了什么结论？",
                    "如何应用文档中的知识？",
                    "文档还涉及哪些相关内容？"
                ]

                while len(questions) < num_questions:
                    questions.append(default_questions[len(questions) % len(default_questions)])

                return questions[:num_questions]

            return [
                "这个文档的主要内容是什么？",
                "文档中提到了哪些核心概念？",
                "能总结一下文档的要点吗？",
                "文档中有什么重要的结论？",
                "解释一下文档中的关键术语"
            ]

        except Exception as e:
            print(f"生成建议问题时出错: {e}")
            return [
                "这个文档的主要内容是什么？",
                "文档中提到了哪些核心概念？",
                "能总结一下文档的要点吗？",
                "文档中有什么重要的结论？",
                "解释一下文档中的关键术语"
            ]
