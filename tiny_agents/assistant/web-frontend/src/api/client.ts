import type {
  InitResponse,
  UploadResponse,
  DocumentLoadResponse,
  ChatResponse,
  NoteResponse,
  StatsResponse,
  ReportResponse,
  RecallResponse,
  InitRequest,
  DocumentLoadRequest,
  ChatRequest,
  NoteRequest,
  RecallRequest,
  ReportRequest,
} from '../types/api';

const API_BASE = '/api';

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: '请求失败',
      }));
      throw new Error(error.detail || error.message || '请求失败');
    }

    return response.json();
  }

  // 初始化助手
  async initAssistant(userId: string): Promise<InitResponse> {
    return this.request<InitResponse>('/init', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId } satisfies InitRequest),
    });
  }

  // 上传 PDF 文件
  async uploadPDF(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: '文件上传失败',
      }));
      throw new Error(error.detail || '文件上传失败');
    }

    return response.json();
  }

  // 加载文档
  async loadDocument(userId: string, filePath: string): Promise<DocumentLoadResponse> {
    return this.request<DocumentLoadResponse>('/document/load', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        file_path: filePath,
      } satisfies DocumentLoadRequest),
    });
  }

  // 智能问答
  async askQuestion(
    userId: string,
    question: string,
    useAdvancedSearch = true
  ): Promise<ChatResponse> {
    return this.request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        question,
        use_advanced_search: useAdvancedSearch,
      } satisfies ChatRequest),
    });
  }

  // 添加笔记
  async addNote(
    userId: string,
    content: string,
    concept?: string
  ): Promise<NoteResponse> {
    return this.request<NoteResponse>('/notes', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        content,
        concept,
      } satisfies NoteRequest),
    });
  }

  // 回忆信息
  async recall(userId: string, query: string, limit = 5): Promise<RecallResponse> {
    return this.request<RecallResponse>('/recall', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        query,
        limit,
      } satisfies RecallRequest),
    });
  }

  // 获取统计信息
  async getStats(userId: string): Promise<StatsResponse> {
    return this.request<StatsResponse>(`/stats?user_id=${encodeURIComponent(userId)}`);
  }

  // 生成报告
  async generateReport(userId: string): Promise<ReportResponse> {
    return this.request<ReportResponse>('/report', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId } satisfies ReportRequest),
    });
  }

  // 健康检查
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string }> {
    return this.request('/health');
  }
}

// 导出单例
export const api = new APIClient();
