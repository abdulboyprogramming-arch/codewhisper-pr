// ============================================================
// CodeWhisper PR - Reviews API Endpoints
// ============================================================

import { apiClient } from '../client';
import { extractData } from '../interceptors';

export interface CreateReviewRequest {
  repository_url: string;
  pr_number: number;
  branch?: string;
  settings?: {
    severity_threshold?: string;
    categories?: string[];
    max_tokens?: number;
    temperature?: number;
  };
}

export interface Review {
  id: string;
  user_id: string;
  repository_url: string;
  repository_name: string;
  pr_number: number;
  pr_title: string | null;
  pr_description: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  diff_content: string | null;
  affected_files: any[] | null;
  original_tokens: number | null;
  optimized_tokens: number | null;
  tokens_saved_percentage: number | null;
  optimization_time_ms: number | null;
  review_output: any | null;
  summary: string | null;
  issues_found: any[] | null;
  model_used: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface ReviewsListResponse {
  items: Review[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface DashboardStats {
  total_reviews: number;
  total_tokens_saved: number;
  average_savings_percentage: number;
  total_cost_saved: number;
  recent_reviews: any[];
  daily_stats: any[];
  top_categories: any[];
}

export const reviewsApi = {
  async createReview(data: CreateReviewRequest): Promise<Review> {
    const response = await apiClient.post<Review>('/reviews/create', data);
    return extractData(response);
  },

  async getReview(id: string): Promise<Review> {
    const response = await apiClient.get<Review>(`/reviews/${id}`);
    return extractData(response);
  },

  async listReviews(params?: {
    page?: number;
    limit?: number;
    status?: string;
    search?: string;
  }): Promise<ReviewsListResponse> {
    const response = await apiClient.get<ReviewsListResponse>('/reviews/', { params });
    return extractData(response);
  },

  async getReviewStatus(id: string): Promise<any> {
    const response = await apiClient.get(`/reviews/${id}/status`);
    return extractData(response);
  },

  async getDashboardStats(): Promise<DashboardStats> {
    const response = await apiClient.get<DashboardStats>('/analytics/dashboard');
    return extractData(response);
  },
};
