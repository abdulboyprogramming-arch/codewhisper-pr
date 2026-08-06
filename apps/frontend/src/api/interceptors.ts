// ============================================================
// CodeWhisper PR - API Interceptors
// ============================================================

import { AxiosError, AxiosResponse } from 'axios';

export interface ApiError {
  message: string;
  status: number;
  data?: any;
}

export function handleApiError(error: AxiosError): Promise<ApiError> {
  const response = error.response;
  const message = response?.data?.detail || response?.data?.message || error.message;
  const status = response?.status || 500;
  const data = response?.data;

  return Promise.reject({ message, status, data });
}

export function extractData<T>(response: AxiosResponse<T>): T {
  return response.data;
}

export function setAuthToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', token);
  }
}

export function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
}

export function removeAuthToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

export function setRefreshToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('refresh_token', token);
  }
}

export function getRefreshToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('refresh_token');
  }
  return null;
}
