import api from './index';
import type { Task, TaskCreate, TaskResponse } from '@/types';

export const taskApi = {
  create: (data: TaskCreate) =>
    api.post<TaskResponse>('/tasks/', data),

  list: () =>
    api.get<TaskResponse[]>('/tasks/'),

  get: (id: string) =>
    api.get<TaskResponse>(`/tasks/${id}`),

  start: (id: string) =>
    api.post(`/tasks/${id}/start`),

  pause: (id: string) =>
    api.post(`/tasks/${id}/pause`),

  cancel: (id: string) =>
    api.post(`/tasks/${id}/cancel`)
};