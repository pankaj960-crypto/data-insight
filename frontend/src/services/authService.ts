import api from './api';
import type { TokenResponse, User } from '../types';

export const authService = {
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post<User>('/auth/register', data),

  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }),

  logout: () => api.post('/auth/logout'),

  getProfile: () => api.get<User>('/auth/me'),

  updateProfile: (data: { full_name?: string; username?: string }) =>
    api.patch<User>('/auth/me', data),
};
