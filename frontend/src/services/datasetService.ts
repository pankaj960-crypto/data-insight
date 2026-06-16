import api from './api';
import type { Analysis, ChartRequest, Dataset, PredictionResult } from '../types';

export const datasetService = {
  upload: (file: File, name?: string) => {
    const form = new FormData();
    form.append('file', file);
    if (name) form.append('name', name);
    return api.post<Dataset>('/datasets/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  list: () => api.get<{ datasets: Dataset[]; total: number }>('/datasets'),

  get: (id: number) => api.get<Dataset>(`/datasets/${id}`),

  getAnalysis: (id: number, refresh = false) =>
    api.get<Analysis>(`/datasets/${id}/analysis`, { params: { refresh } }),

  preview: (id: number, rows = 20) =>
    api.get<{ columns: string[]; data: Record<string, string>[]; total_rows: number }>(
      `/datasets/${id}/preview`,
      { params: { rows } }
    ),

  delete: (id: number) => api.delete(`/datasets/${id}`),

  createChart: (id: number, config: ChartRequest) =>
    api.post<{ chart_type: string; plotly_json: object }>(`/charts/${id}`, config),

  chat: (id: number, message: string, history?: { role: string; content: string }[]) =>
    api.post<{ reply: string; suggestions: string[] }>(`/chat/${id}`, { message, history }),

  predict: (id: number, config: {
    task_type: string;
    target_column: string;
    feature_columns?: string[];
    model_type?: string;
  }) => api.post<PredictionResult>(`/predictions/${id}`, config),

  cleanPreview: (id: number, operations: object[]) =>
    api.post(`/cleaning/${id}/preview`, { operations }),

  cleanApply: (id: number, operations: object[], apply = true) =>
    api.post(`/cleaning/${id}/apply`, { operations, apply }),

  exportReport: (id: number, format: string, title?: string) =>
    api.post(`/reports/${id}/export`, null, { params: { format, title } }),

  getDashboard: () => api.get('/dashboard'),
};
