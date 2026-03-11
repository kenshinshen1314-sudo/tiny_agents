# PDFParserAssistant Web 应用

智能文档问答助手 - 基于 RAG 的 PDF 文档解析和问答系统。

## 功能特性

- 🚀 **助手初始化**: 基于用户 ID 创建独立的助手实例
- 📄 **文档加载**: 上传 PDF 文档并加载到 RAG 知识库
- 💬 **智能问答**: 基于文档内容进行语义搜索和问答
- 📝 **学习笔记**: 记录学习心得和概念笔记
- 📊 **智能统计**: 查看会话统计和生成学习报告

## 项目结构

```
tiny_agents/assistant/
├── PDFParserAssistant.py    # 核心助手类
├── web/                      # 后端 FastAPI 服务
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── api.py               # API 路由定义
│   ├── manager.py           # 助手实例管理器
│   └── report/              # 报告输出目录
└── web-frontend/            # 前端 React 应用
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/
        │   └── client.ts
        ├── components/
        │   ├── Header.tsx
        │   ├── TabsPanel.tsx
        │   ├── InitTab.tsx
        │   ├── ChatTab.tsx
        │   ├── NotesTab.tsx
        │   └── StatsTab.tsx
        ├── hooks/
        │   └── useAssistant.ts
        └── types/
            └── api.ts
```

## 环境要求

- Python 3.8+
- Node.js 18+
- pip 和 npm/yarn

## 安装依赖

### 后端依赖

```bash
cd /Users/kenshin/Projects/my-first-agent
pip install -r requirements.txt
```

后端依赖包括：
- `fastapi>=0.109.0` - Web 框架
- `uvicorn[standard]>=0.27.0` - ASGI 服务器
- `python-multipart>=0.0.6` - 文件上传支持
- `aiofiles>=23.2.1` - 异步文件操作

### 前端依赖

```bash
cd tiny_agents/assistant/web-frontend
npm install
```

## 启动服务

### 1. 启动后端服务

```bash
# 从项目根目录启动
cd /Users/kenshin/Projects/my-first-agent
uvicorn tiny_agents.assistant.LearningAssistant.web.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将运行在 `http://localhost:8000`

API 文档: `http://localhost:8000/docs`

### 2. 启动前端服务

```bash
cd tiny_agents/assistant/web-frontend
npm run dev
```

前端服务将运行在 `http://localhost:5173`

## 使用指南

### 1. 初始化助手

在"初始化 & 资料"标签页：
1. 输入用户 ID（例如：user123）
2. 点击"初始化助手"按钮

### 2. 上传和加载文档

1. 点击上传区域选择 PDF 文件
2. 文件上传成功后点击"加载文档到知识库"
3. 等待文档加载完成

### 3. 智能问答

切换到"智能问答"标签页：
1. 输入问题或点击示例问题
2. 系统将基于文档内容返回答案

### 4. 添加学习笔记

在"学习笔记"标签页：
1. 输入笔记内容
2. 可选：输入相关概念
3. 点击"保存笔记"

### 5. 查看统计和生成报告

在"智能统计"标签页：
1. 点击"实时刷新"获取当前统计
2. 点击"生成报告"导出学习报告

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/init` | POST | 初始化助手 |
| `/api/upload` | POST | 上传 PDF 文件 |
| `/api/document/load` | POST | 加载文档 |
| `/api/chat` | POST | 智能问答 |
| `/api/notes` | POST | 添加笔记 |
| `/api/recall` | POST | 回忆信息 |
| `/api/stats` | GET | 获取统计 |
| `/api/report` | POST | 生成报告 |
| `/api/health` | GET | 健康检查 |

## 技术栈

### 后端
- FastAPI - 现代化的 Python Web 框架
- Uvicorn - ASGI 服务器
- Pydantic - 数据验证

### 前端
- React 18 - UI 框架
- TypeScript - 类型安全
- Vite - 构建工具
- Tailwind CSS - 样式框架
- Zustand - 状态管理
- Lucide React - 图标库

## 开发说明

### 添加新的 API 端点

1. 在 `web/api.py` 中定义新的路由
2. 在 `src/types/api.ts` 中添加类型定义
3. 在 `src/api/client.ts` 中添加客户端方法
4. 在 `src/hooks/useAssistant.ts` 中添加状态管理

### 添加新的组件

1. 在 `src/components/` 中创建新组件
2. 在 `TabsPanel.tsx` 中添加新的标签页
3. 按需在 `useAssistant` hook 中添加状态

## 故障排除

### 后端启动失败

检查端口 8000 是否被占用：
```bash
lsof -i :8000
```

### 前端连接失败

确保后端服务已启动，并检查 CORS 配置。

### PDF 加载失败

检查 PDF 文件格式是否正确，确保文件没有损坏。

## 许可证

本项目采用 MIT 许可证。
