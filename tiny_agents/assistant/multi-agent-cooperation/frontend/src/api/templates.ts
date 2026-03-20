import api from './index';
import type { TeamTemplate, AnalyzeResult } from '@/types';

export const templateApi = {
  list: () =>
    api.get<TeamTemplate[]>('/templates/'),

  get: (id: string) =>
    api.get<TeamTemplate>(`/templates/${id}`),

  analyze: (userInput: string) =>
    api.post<AnalyzeResult>('/templates/analyze', userInput, {
      headers: { 'Content-Type': 'text/plain' }
    })
};