export type TaskStatus =
  | 'pending'
  | 'analyzing'
  | 'team_building'
  | 'executing'
  | 'completed'
  | 'failed'
  | 'paused';

export type TaskType = 'dev' | 'writing';

export type TaskComplexity = 'simple' | 'normal' | 'complex';

export interface Task {
  id: string;
  user_input: string;
  task_type?: TaskType;
  complexity?: TaskComplexity;
  status: TaskStatus;
  template_id?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  progress: number;
  cost: number;
}

export interface TaskCreate {
  user_input: string;
}

export interface TaskResponse {
  id: string;
  status: TaskStatus;
  progress: number;
  message?: string;
}

export interface TeamTemplate {
  id: string;
  name: string;
  description: string;
  task_type: string;
  roles: string[];
  execution_flow: Array<{
    step: number;
    role?: string;
    roles?: string[];
    parallel?: boolean;
  }>;
}

export interface AnalyzeResult {
  task_type: TaskType;
  complexity: TaskComplexity;
  recommended_template: string;
  available_templates: string[];
}

export interface Role {
  name: string;
  status: 'idle' | 'waiting' | 'working' | 'completed' | 'failed';
  output?: any;
}