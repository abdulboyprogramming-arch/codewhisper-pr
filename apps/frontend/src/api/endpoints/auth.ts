// ============================================================
// CodeWhisper PR - Auth API Endpoints
// ============================================================

import { apiClient } from '../client';
import { extractData, setAuthToken, setRefreshToken, removeAuthToken } from '../interceptors';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  fullName?: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  fullName: string | null;
  role: string;
  isActive: boolean;
  isVerified: boolean;
  totalTokensSaved: number;
  totalReviewsCount: number;
  createdAt: string;
  updatedAt: string;
  lastLogin: string | null;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
    const data = extractData(response);
    setAuthToken(data.access_token);
    setRefreshToken(data.refresh_token);
    return data;
  },

  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data);
    return extractData(response);
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      removeAuthToken();
    }
  },

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    const data = extractData(response);
    setAuthToken(data.access_token);
    setRefreshToken(data.refresh_token);
    return data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return extractData(response);
  },
};
