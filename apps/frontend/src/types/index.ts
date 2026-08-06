// ============================================================
// CodeWhisper PR - Types
// ============================================================

// API Response Types
export interface ApiResponse<T> {
  data: T;
  status: string;
  message?: string;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// User / Auth Types
export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string | null;
  role: 'user' | 'admin' | 'super_admin';
  is_active: boolean;
  is_verified: boolean;
  total_tokens_saved: number;
  total_reviews_count: number;
  created_at: string;
  updated_at: string;
  last_login?: string | null;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse extends Token {
  user: User;
}

// Review / Analysis Types
export type ReviewStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface ReviewSettings {
  severityThreshold: 'low' | 'medium' | 'high';
  categories: string[];
  maxTokens: number;
  temperature: number;
}

export interface CreateReviewRequest {
  repositoryUrl: string;
  prNumber: number;
  branch?: string;
  settings?: Partial<ReviewSettings>;
}

export interface Review {
  id: string;
  userId: string;
  repositoryUrl: string;
  repositoryName: string;
  prNumber: number;
  prTitle?: string | null;
  prDescription?: string | null;
  status: ReviewStatus;
  diffContent?: string | null;
  affectedFiles?: any[] | null;
  originalTokens?: number | null;
  optimizedTokens?: number | null;
  tokensSavedPercentage?: number | null;
  optimizationTimeMs?: number | null;
  reviewOutput?: any | null;
  summary?: string | null;
  issuesFound?: any[] | null;
  modelUsed?: string | null;
  createdAt: string;
  updatedAt: string;
  completedAt?: string | null;
}

export interface ReviewsListResponse {
  items: Review[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Analytics Types
export interface DashboardStats {
  totalReviews: number;
  totalTokensSaved: number;
  averageSavingsPercentage: number;
  totalCostSaved: number;
  recentReviews: Review[];
  dailyStats: { date: string; tokens_saved: number; reviews_count: number }[];
  topCategories: { category: string; count: number }[];
}

export interface TokenSavingsTrend {
  labels: string[];
  values: number[];
  period: string;
}

export interface ReviewDistribution {
  labels: string[];
  values: number[];
  percentages: number[];
}
