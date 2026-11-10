import api from './api';
import { AuthResponse, User } from '../types';

export const authService = {
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', { email, password });
    localStorage.setItem('fraudshield_token', response.data.access_token);
    localStorage.setItem('fraudshield_user', JSON.stringify(response.data.user));
    return response.data;
  },

  async register(
    emailOrPayload: string | { email: string; password: string; full_name: string; role?: string },
    fullName?: string,
    password?: string,
    role = 'INVESTIGATOR'
  ): Promise<any> {
    let payload;
    if (typeof emailOrPayload === 'object') {
      payload = emailOrPayload;
    } else {
      payload = {
        email: emailOrPayload,
        full_name: fullName,
        password,
        role,
      };
    }
    const response = await api.post<User>('/auth/register', payload);
    return { user: response.data, ...response.data };
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    localStorage.setItem('fraudshield_user', JSON.stringify(response.data));
    return response.data;
  },

  logout(): void {
    localStorage.removeItem('fraudshield_token');
    localStorage.removeItem('fraudshield_user');
  },

  getStoredUser(): User | null {
    const userStr = localStorage.getItem('fraudshield_user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('fraudshield_token');
  },
};

export default authService;
