export interface InitResponse {
  success: boolean;
  session_id: string;
  user_id: string;
  message: string;
}

export interface UploadResponse {
  success: boolean;
  file_path: string;
  filename: string;
  size: number;
  message: string;
}

export interface DocumentLoadResponse {
  success: boolean;
  message: string;
  document?: string;
}

export interface ChatResponse {
  answer: string;
  duration_ms: number;
  timestamp: string;
}

export interface NoteResponse {
  success: boolean;
  message: string;
  concept: string;
}

export interface StatsResponse {
  [key: string]: string | number;
}

export interface ReportResponse {
  success: boolean;
  report: any;
  message: string;
}

export interface RecallResponse {
  result: string;
  query: string;
}

// API 请求类型
export interface InitRequest {
  user_id: string;
}

export interface DocumentLoadRequest {
  user_id: string;
  file_path: string;
}

export interface ChatRequest {
  user_id: string;
  question: string;
  use_advanced_search?: boolean;
}

export interface NoteRequest {
  user_id: string;
  content: string;
  concept?: string;
}

export interface RecallRequest {
  user_id: string;
  query: string;
  limit?: number;
}

export interface ReportRequest {
  user_id: string;
}

// 消息类型
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface Note {
  id: string;
  content: string;
  concept?: string;
  timestamp: Date;
}
