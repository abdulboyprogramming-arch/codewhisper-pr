// ============================================================
// CodeWhisper PR - API Types
// ============================================================

import { Review, User, TokenUsage, Analytics } from './models';

// ============================================================
// Request Types
// ============================================================

export interface CreateReviewRequest {
  repositoryUrl: string;
  prNumber: number;
  branch?: string;
  settings?: ReviewSettings;
}

export interface ReviewSettings {
  severityThreshold?: 'low' | 'medium' | 'high';
  categories?: ReviewCategory[];
  maxTokens?: number;
  temperature?: number;
}

export type ReviewCategory =
  | 'security'
  | 'performance'
  | 'logic'
  | 'style'
  | 'best_practices';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  fullName?: string;
}

export interface TokenOptimizationRequest {
  context: string;
  maxTokens?: number;
  preserveCodeStructure?: boolean;
}

// ============================================================
// Response Types
// ============================================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface ReviewResponse {
  review: Review;
  tokenSavings: TokenSavings;
}

export interface TokenSavings {
  originalTokens: number;
  optimizedTokens: number;
  savingsPercentage: number;
  costSaved: number;
  optimizationTimeMs: number;
}

export interface AnalyticsResponse {
  totalReviews: number;
  totalTokensSaved: number;
  averageSavingsPercentage: number;
  totalCostSaved: number;
  recentReviews: Review[];
  dailyStats: DailyStats[];
  topCategories: CategoryStats[];
}

export interface DailyStats {
  date: string;
  reviewsCount: number;
  tokensSaved: number;
  savingsPercentage: number;
}

export interface CategoryStats {
  category: ReviewCategory;
  count: number;
  percentage: number;
}

// ============================================================
// Webhook Types
// ============================================================

export interface GitHubWebhookPayload {
  action: string;
  number: number;
  pull_request: {
    url: string;
    title: string;
    body: string;
    html_url: string;
    diff_url: string;
    patch_url: string;
    head: {
      ref: string;
      sha: string;
      repo: {
        full_name: string;
        clone_url: string;
      };
    };
    base: {
      ref: string;
      sha: string;
    };
  };
  repository: {
    name: string;
    full_name: string;
    html_url: string;
    clone_url: string;
  };
  sender: {
    login: string;
    avatar_url: string;
  };
}
