import { create } from 'zustand';
import type {
  ChatMessage,
  Note,
  StatsResponse,
} from '../types/api';
import { api } from '../api/client';

interface AssistantState {
  // 用户信息
  userId: string;
  sessionId: string;
  isInitialized: boolean;

  // 文档状态
  uploadedFilePath: string | null;
  uploadedFileName: string | null;
  loadedDocument: string | null;
  isLoadingDocument: boolean;

  // 聊天状态
  messages: ChatMessage[];
  isAsking: boolean;

  // 笔记状态
  notes: Note[];
  isSavingNote: boolean;

  // 统计信息
  stats: StatsResponse | null;
  isLoadingStats: boolean;

  // 错误状态
  error: string | null;

  // Actions
  setUserId: (userId: string) => void;
  initialize: () => Promise<void>;
  uploadPDF: (file: File) => Promise<void>;
  loadDocument: () => Promise<void>;
  askQuestion: (question: string) => Promise<void>;
  addNote: (content: string, concept?: string) => Promise<void>;
  getStats: () => Promise<void>;
  generateReport: () => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

export const useAssistant = create<AssistantState>((set, get) => ({
  // 初始状态
  userId: '',
  sessionId: '',
  isInitialized: false,

  uploadedFilePath: null,
  uploadedFileName: null,
  loadedDocument: null,
  isLoadingDocument: false,

  messages: [],
  isAsking: false,

  notes: [],
  isSavingNote: false,

  stats: null,
  isLoadingStats: false,

  error: null,

  // 设置用户 ID
  setUserId: (userId: string) => set({ userId }),

  // 初始化助手
  initialize: async () => {
    const { userId } = get();
    if (!userId) {
      set({ error: '请输入用户 ID' });
      return;
    }

    try {
      const response = await api.initAssistant(userId);
      set({
        sessionId: response.session_id,
        isInitialized: true,
        error: null,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '初始化失败',
        isInitialized: false,
      });
    }
  },

  // 上传 PDF
  uploadPDF: async (file: File) => {
    try {
      const response = await api.uploadPDF(file);
      set({
        uploadedFilePath: response.file_path,
        uploadedFileName: response.filename,
        error: null,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '文件上传失败',
      });
    }
  },

  // 加载文档
  loadDocument: async () => {
    const { userId, uploadedFilePath } = get();
    if (!userId || !uploadedFilePath) {
      set({ error: '请先上传文件' });
      return;
    }

    set({ isLoadingDocument: true });

    try {
      const response = await api.loadDocument(userId, uploadedFilePath);
      set({
        loadedDocument: response.document || null,
        error: null,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '文档加载失败',
      });
    } finally {
      set({ isLoadingDocument: false });
    }
  },

  // 提问
  askQuestion: async (question: string) => {
    const { userId, messages } = get();
    if (!userId) {
      set({ error: '请先初始化助手' });
      return;
    }

    // 添加用户消息
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    };
    set({ messages: [...messages, userMessage], isAsking: true });

    try {
      const response = await api.askQuestion(userId, question);

      // 添加助手回复
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
      };
      set({
        messages: [...get().messages, assistantMessage],
        error: null,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '问答失败',
      });
    } finally {
      set({ isAsking: false });
    }
  },

  // 添加笔记
  addNote: async (content: string, concept?: string) => {
    const { userId, notes } = get();
    if (!userId) {
      set({ error: '请先初始化助手' });
      return;
    }

    set({ isSavingNote: true });

    try {
      await api.addNote(userId, content, concept);

      const newNote: Note = {
        id: Date.now().toString(),
        content,
        concept,
        timestamp: new Date(),
      };
      set({
        notes: [...notes, newNote],
        error: null,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '添加笔记失败',
      });
    } finally {
      set({ isSavingNote: false });
    }
  },

  // 获取统计信息
  getStats: async () => {
    const { userId } = get();
    if (!userId) {
      set({ error: '请先初始化助手' });
      return;
    }

    set({ isLoadingStats: true });

    try {
      const stats = await api.getStats(userId);
      set({ stats, error: null });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '获取统计失败',
      });
    } finally {
      set({ isLoadingStats: false });
    }
  },

  // 生成报告
  generateReport: async () => {
    const { userId } = get();
    if (!userId) {
      set({ error: '请先初始化助手' });
      return;
    }

    try {
      const response = await api.generateReport(userId);
      set({ error: null });
      alert(`报告生成成功！\n文件: ${response.report.report_file}`);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '生成报告失败',
      });
    }
  },

  // 清除错误
  clearError: () => set({ error: null }),

  // 重置状态
  reset: () => set({
    userId: '',
    sessionId: '',
    isInitialized: false,
    uploadedFilePath: null,
    uploadedFileName: null,
    loadedDocument: null,
    isLoadingDocument: false,
    messages: [],
    isAsking: false,
    notes: [],
    isSavingNote: false,
    stats: null,
    isLoadingStats: false,
    error: null,
  }),
}));
